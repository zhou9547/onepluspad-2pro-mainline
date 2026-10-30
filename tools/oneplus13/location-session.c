// SPDX-License-Identifier: GPL-2.0-only
/*
 * Keep one QRTR LOC client across setup, start, NMEA indications, and stop.
 * qmicli executes one request per process, which closes the QRTR client even
 * when --client-no-release-cid is used.
 */

#include <gio/gio.h>
#include <glib-unix.h>
#include <libqmi-glib.h>
#include <stdio.h>
#include <stdlib.h>

struct session {
	GMainLoop *loop;
	GCancellable *cancellable;
	QmiDevice *device;
	QmiClientLoc *client;
	guint timeout_id;
	guint nmea_count;
	guint requested_seconds;
	gboolean started;
	gboolean stopped;
};

static int exit_status = 1;

static void
finish (struct session *session, int status)
{
	exit_status = status;
	if (session->timeout_id)
		g_source_remove (session->timeout_id);
	if (session->loop && g_main_loop_is_running (session->loop))
		g_main_loop_quit (session->loop);
}

static void
print_error (const char *operation, const GError *error)
{
	g_printerr ("LOCATION_SESSION_ERROR operation=%s error=%s\n",
		    operation, error ? error->message : "unknown");
}

static void
nmea_received (QmiClientLoc *client,
	       QmiIndicationLocNmeaOutput *output,
	       gpointer user_data)
{
	struct session *session = user_data;
	const char *nmea = NULL;

	(void)client;
	if (qmi_indication_loc_nmea_output_get_nmea_string (output, &nmea, NULL) &&
	    nmea) {
		session->nmea_count++;
		g_print ("NMEA %s\n", nmea);
		fflush (stdout);
	}
}

static gboolean
request_stop (gpointer user_data);

static void
stop_ready (QmiClientLoc *client, GAsyncResult *result, gpointer user_data)
{
	struct session *session = user_data;
	QmiMessageLocStopOutput *output;
	GError *error = NULL;

	output = qmi_client_loc_stop_finish (client, result, &error);
	if (!output) {
		print_error ("stop", error);
		g_clear_error (&error);
		finish (session, 1);
		return;
	}
	if (!qmi_message_loc_stop_output_get_result (output, &error)) {
		print_error ("stop-result", error);
		g_clear_error (&error);
		qmi_message_loc_stop_output_unref (output);
		finish (session, 1);
		return;
	}
	qmi_message_loc_stop_output_unref (output);
	session->stopped = TRUE;
	g_print ("LOCATION_SESSION_STOPPED nmea=%u\n", session->nmea_count);
	finish (session, session->started ? 0 : 1);
}

static gboolean
request_stop (gpointer user_data)
{
	struct session *session = user_data;
	QmiMessageLocStopInput *input;

	session->timeout_id = 0;
	input = qmi_message_loc_stop_input_new ();
	qmi_message_loc_stop_input_set_session_id (input, 1, NULL);
	qmi_client_loc_stop (session->client, input, 20,
			     session->cancellable,
			     (GAsyncReadyCallback) stop_ready, session);
	qmi_message_loc_stop_input_unref (input);
	return G_SOURCE_REMOVE;
}

static void
start_ready (QmiClientLoc *client, GAsyncResult *result, gpointer user_data)
{
	struct session *session = user_data;
	QmiMessageLocStartOutput *output;
	GError *error = NULL;

	output = qmi_client_loc_start_finish (client, result, &error);
	if (!output) {
		print_error ("start", error);
		g_clear_error (&error);
		finish (session, 1);
		return;
	}
	if (!qmi_message_loc_start_output_get_result (output, &error)) {
		print_error ("start-result", error);
		g_clear_error (&error);
		qmi_message_loc_start_output_unref (output);
		finish (session, 1);
		return;
	}
	qmi_message_loc_start_output_unref (output);
	session->started = TRUE;
	g_print ("LOCATION_SESSION_STARTED seconds=%u\n", session->requested_seconds);
	fflush (stdout);
	session->timeout_id =
		g_timeout_add_seconds (session->requested_seconds, request_stop,
				       session);
}

static void
register_events_ready (QmiClientLoc *client, GAsyncResult *result,
		       gpointer user_data)
{
	struct session *session = user_data;
	QmiMessageLocRegisterEventsOutput *output;
	QmiMessageLocStartInput *input;
	GError *error = NULL;

	output = qmi_client_loc_register_events_finish (client, result, &error);
	if (!output) {
		print_error ("register-events", error);
		g_clear_error (&error);
		finish (session, 1);
		return;
	}
	if (!qmi_message_loc_register_events_output_get_result (output, &error)) {
		print_error ("register-events-result", error);
		g_clear_error (&error);
		qmi_message_loc_register_events_output_unref (output);
		finish (session, 1);
		return;
	}
	qmi_message_loc_register_events_output_unref (output);

	input = qmi_message_loc_start_input_new ();
	qmi_message_loc_start_input_set_session_id (input, 1, NULL);
	qmi_message_loc_start_input_set_intermediate_report_state (
		input, QMI_LOC_INTERMEDIATE_REPORT_STATE_ENABLE, NULL);
	qmi_message_loc_start_input_set_minimum_interval_between_position_reports (
		input, 1000, NULL);
	qmi_message_loc_start_input_set_fix_recurrence_type (
		input, QMI_LOC_FIX_RECURRENCE_TYPE_REQUEST_PERIODIC_FIXES, NULL);
	qmi_client_loc_start (client, input, 20, session->cancellable,
			      (GAsyncReadyCallback) start_ready, session);
	qmi_message_loc_start_input_unref (input);
}

static void
set_nmea_ready (QmiClientLoc *client, GAsyncResult *result, gpointer user_data)
{
	struct session *session = user_data;
	QmiMessageLocSetNmeaTypesOutput *output;
	QmiMessageLocRegisterEventsInput *input;
	GError *error = NULL;

	output = qmi_client_loc_set_nmea_types_finish (client, result, &error);
	if (!output) {
		print_error ("set-nmea", error);
		g_clear_error (&error);
		finish (session, 1);
		return;
	}
	if (!qmi_message_loc_set_nmea_types_output_get_result (output, &error)) {
		print_error ("set-nmea-result", error);
		g_clear_error (&error);
		qmi_message_loc_set_nmea_types_output_unref (output);
		finish (session, 1);
		return;
	}
	qmi_message_loc_set_nmea_types_output_unref (output);

	input = qmi_message_loc_register_events_input_new ();
	qmi_message_loc_register_events_input_set_event_registration_mask (
		input, QMI_LOC_EVENT_REGISTRATION_FLAG_NMEA, NULL);
	qmi_client_loc_register_events (
		client, input, 20, session->cancellable,
		(GAsyncReadyCallback) register_events_ready, session);
	qmi_message_loc_register_events_input_unref (input);
}

static void
client_ready (QmiDevice *device, GAsyncResult *result, gpointer user_data)
{
	struct session *session = user_data;
	QmiMessageLocSetNmeaTypesInput *input;
	GError *error = NULL;

	session->client = QMI_CLIENT_LOC (
		qmi_device_allocate_client_finish (device, result, &error));
	if (!session->client) {
		print_error ("allocate-client", error);
		g_clear_error (&error);
		finish (session, 1);
		return;
	}
	g_signal_connect (session->client, "nmea",
			  G_CALLBACK (nmea_received), session);
	input = qmi_message_loc_set_nmea_types_input_new ();
	qmi_message_loc_set_nmea_types_input_set_nmea_types (
		input, QMI_LOC_NMEA_TYPE_GGA | QMI_LOC_NMEA_TYPE_RMC, NULL);
	qmi_client_loc_set_nmea_types (
		session->client, input, 20, session->cancellable,
		(GAsyncReadyCallback) set_nmea_ready, session);
	qmi_message_loc_set_nmea_types_input_unref (input);
}

static void
device_open_ready (QmiDevice *device, GAsyncResult *result, gpointer user_data)
{
	struct session *session = user_data;
	GError *error = NULL;

	if (!qmi_device_open_finish (device, result, &error)) {
		print_error ("open-device", error);
		g_clear_error (&error);
		finish (session, 1);
		return;
	}
	qmi_device_allocate_client (
		device, QMI_SERVICE_LOC, QMI_CID_NONE, 20,
		session->cancellable, (GAsyncReadyCallback) client_ready, session);
}

static void
device_ready (GObject *source, GAsyncResult *result, gpointer user_data)
{
	struct session *session = user_data;
	GError *error = NULL;

	(void)source;
	session->device = qmi_device_new_from_node_finish (result, &error);
	if (!session->device) {
		print_error ("create-device", error);
		g_clear_error (&error);
		finish (session, 1);
		return;
	}
	qmi_device_open (session->device,
			 QMI_DEVICE_OPEN_FLAGS_EXPECT_INDICATIONS,
			 20, session->cancellable,
			 (GAsyncReadyCallback) device_open_ready, session);
}

static void
bus_ready (GObject *source, GAsyncResult *result, gpointer user_data)
{
	struct session *session = user_data;
	QrtrBus *bus;
	QrtrNode *node;
	GError *error = NULL;

	(void)source;
	bus = qrtr_bus_new_finish (result, &error);
	if (!bus) {
		print_error ("open-qrtr", error);
		g_clear_error (&error);
		finish (session, 1);
		return;
	}
	node = qrtr_bus_peek_node (bus, 0);
	if (!node) {
		g_printerr ("LOCATION_SESSION_ERROR operation=find-node\n");
		g_object_unref (bus);
		finish (session, 1);
		return;
	}
	qmi_device_new_from_node (node, session->cancellable,
				  (GAsyncReadyCallback) device_ready, session);
	g_object_unref (bus);
}

static gboolean
terminate (gpointer user_data)
{
	struct session *session = user_data;
	if (session->client && session->started && !session->stopped)
		request_stop (session);
	else
		finish (session, 1);
	return G_SOURCE_REMOVE;
}

int
main (int argc, char **argv)
{
	struct session session = { 0 };
	unsigned int seconds = 45;

	if (argc == 3 && g_str_equal (argv[1], "--seconds"))
		seconds = (unsigned int) g_ascii_strtoull (argv[2], NULL, 10);
	else if (argc != 1) {
		g_printerr ("usage: %s [--seconds SECONDS]\n", argv[0]);
		return 2;
	}
	if (seconds < 5 || seconds > 180)
		return 2;

	session.requested_seconds = seconds;
	session.loop = g_main_loop_new (NULL, FALSE);
	session.cancellable = g_cancellable_new ();
	g_unix_signal_add (SIGINT, terminate, &session);
	g_unix_signal_add (SIGTERM, terminate, &session);
	g_timeout_add_seconds (seconds + 45, terminate, &session);
	qrtr_bus_new (5000, session.cancellable,
		      (GAsyncReadyCallback) bus_ready, &session);
	g_main_loop_run (session.loop);

	if (session.device)
		qmi_device_close_async (session.device, 5, session.cancellable,
					NULL, NULL);
	if (session.client)
		g_object_unref (session.client);
	if (session.device)
		g_object_unref (session.device);
	g_object_unref (session.cancellable);
	g_main_loop_unref (session.loop);
	return exit_status;
}
