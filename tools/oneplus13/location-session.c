// SPDX-License-Identifier: GPL-2.0-only
/*
 * Keep one QRTR LOC client across setup, start, NMEA indications, and stop.
 * qmicli executes one request per process, which closes the QRTR client even
 * when --client-no-release-cid is used.
 */

#include <gio/gio.h>
#include <glib-unix.h>
#include <libqmi-glib.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

struct session {
	GMainLoop *loop;
	GCancellable *cancellable;
	QmiDevice *device;
	QmiClientLoc *client;
	guint timeout_id;
	guint deadline_id;
	guint nmea_count;
	guint requested_seconds;
	gboolean started;
	gboolean start_requested;
	gboolean start_pending;
	gboolean terminate_requested;
	gboolean stopped;
	gboolean stop_requested;
	gboolean position_events_only;
};

static int exit_status = 1;
static gboolean terminate (gpointer user_data);
static gboolean unix_terminate (gpointer user_data);

static gboolean
claim_stop (struct session *session)
{
	if (session->stop_requested)
		return FALSE;
	session->stop_requested = TRUE;
	if (session->timeout_id) {
		g_source_remove (session->timeout_id);
		session->timeout_id = 0;
	}
	return TRUE;
}

static gboolean
self_test_timer (gpointer user_data)
{
	(void)user_data;
	return G_SOURCE_CONTINUE;
}

static gboolean
nmea_types_error_is_optional (const GError *error)
{
	return g_error_matches (error, QMI_PROTOCOL_ERROR,
				QMI_PROTOCOL_ERROR_NOT_SUPPORTED);
}

static gboolean
retry_position_events (const GError *error, gboolean already_retried)
{
	return !already_retried && g_error_matches (error, QMI_PROTOCOL_ERROR,
						 QMI_PROTOCOL_ERROR_INVALID_ARGUMENT);
}

static int
configuration_self_test (void)
{
	GError *unsupported;
	GError *general;
	GError *transport;
	GError *invalid;
	struct session session = { 0 };
	struct session pending = { .start_pending = TRUE };
	guint timer_id;

	unsupported = g_error_new_literal (QMI_PROTOCOL_ERROR,
		QMI_PROTOCOL_ERROR_NOT_SUPPORTED, "unsupported configuration");
	general = g_error_new_literal (QMI_PROTOCOL_ERROR,
		QMI_PROTOCOL_ERROR_GENERAL_ERROR, "modem failure");
	transport = g_error_new_literal (G_IO_ERROR,
		QMI_PROTOCOL_ERROR_NOT_SUPPORTED, "different error domain");
	invalid = g_error_new_literal (QMI_PROTOCOL_ERROR,
		QMI_PROTOCOL_ERROR_INVALID_ARGUMENT, "unsupported NMEA event");
	g_assert_true (nmea_types_error_is_optional (unsupported));
	g_assert_false (nmea_types_error_is_optional (general));
	g_assert_false (nmea_types_error_is_optional (transport));
	g_assert_false (nmea_types_error_is_optional (NULL));
	g_assert_true (retry_position_events (invalid, FALSE));
	g_assert_false (retry_position_events (invalid, TRUE));
	g_assert_false (retry_position_events (general, FALSE));
	g_assert_false (retry_position_events (transport, FALSE));
	g_assert_false (retry_position_events (NULL, FALSE));
	g_error_free (invalid);
	g_error_free (unsupported);
	g_error_free (general);
	g_error_free (transport);
	timer_id = g_timeout_add_seconds (3600, self_test_timer, NULL);
	session.timeout_id = timer_id;
	g_assert_true (claim_stop (&session));
	g_assert_cmpuint (session.timeout_id, ==, 0);
	g_assert_null (g_main_context_find_source_by_id (NULL, timer_id));
	g_assert_false (claim_stop (&session));
	g_assert_false (terminate (&session));
	g_assert_false (terminate (&pending));
	g_assert_true (pending.terminate_requested);
	g_assert_false (pending.stop_requested);
	g_assert_true (unix_terminate (&session));
	g_assert_true (unix_terminate (&pending));
	g_print ("LOCATION_SESSION_CONFIG_SELF_TEST_PASS checks=19 no_qrtr=1\n");
	return 0;
}

static void
finish (struct session *session, int status)
{
	exit_status = status;
	if (session->timeout_id) {
		g_source_remove (session->timeout_id);
		session->timeout_id = 0;
	}
	if (session->deadline_id) {
		g_source_remove (session->deadline_id);
		session->deadline_id = 0;
	}
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
position_received (QmiClientLoc *client,
		   QmiIndicationLocPositionReportOutput *output, gpointer user_data)
{
	QmiLocSessionStatus status;
	QmiLocTechnologyUsed technology;
	gdouble latitude, longitude;

	(void)client;
	(void)user_data;
	/* A fused/network estimate or an intermediate report cannot qualify GNSS. */
	if (!qmi_indication_loc_position_report_output_get_session_status (output, &status, NULL) ||
	    status != QMI_LOC_SESSION_STATUS_SUCCESS ||
	    !qmi_indication_loc_position_report_output_get_technology_used (output, &technology, NULL) ||
	    !(technology & QMI_LOC_TECHNOLOGY_USED_SATELLITE) ||
	    !qmi_indication_loc_position_report_output_get_latitude (output, &latitude, NULL) ||
	    !qmi_indication_loc_position_report_output_get_longitude (output, &longitude, NULL) ||
	    !isfinite (latitude) || !isfinite (longitude) ||
	    latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180)
		return;
	g_print ("LOCATION_SESSION_POSITION {\"status\":\"success\",\"satellite\":true,"
		 "\"latitude\":%.9f,\"longitude\":%.9f}\n", latitude, longitude);
	fflush (stdout);
}

static void register_events (struct session *session);

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

	if (!claim_stop (session))
		return G_SOURCE_REMOVE;
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
	session->start_pending = FALSE;
	if (!output) {
		print_error ("start", error);
		g_clear_error (&error);
		/* A lost reply does not prove that the modem rejected start. */
		request_stop (session);
		return;
	}
	if (!qmi_message_loc_start_output_get_result (output, &error)) {
		print_error ("start-result", error);
		g_clear_error (&error);
		qmi_message_loc_start_output_unref (output);
		request_stop (session);
		return;
	}
	qmi_message_loc_start_output_unref (output);
	session->started = TRUE;
	g_print ("LOCATION_SESSION_STARTED seconds=%u\n", session->requested_seconds);
	fflush (stdout);
	if (session->terminate_requested)
		request_stop (session);
	else if (!session->stop_requested)
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
		if (retry_position_events (error, session->position_events_only)) {
			/* Some firmware rejects the optional NMEA event. Use the
			 * standard LOC position report on this same client, once. */
			session->position_events_only = TRUE;
			g_print ("LOCATION_SESSION_POSITION_EVENTS reason=nmea-invalid-argument\n");
			g_clear_error (&error);
			qmi_message_loc_register_events_output_unref (output);
			register_events (session);
			return;
		}
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
	session->start_requested = TRUE;
	session->start_pending = TRUE;
	qmi_client_loc_start (client, input, 20, session->cancellable,
			      (GAsyncReadyCallback) start_ready, session);
	qmi_message_loc_start_input_unref (input);
}

static void
register_events (struct session *session)
{
	QmiMessageLocRegisterEventsInput *input;
	input = qmi_message_loc_register_events_input_new ();
	qmi_message_loc_register_events_input_set_event_registration_mask (
		input, session->position_events_only ?
		QMI_LOC_EVENT_REGISTRATION_FLAG_POSITION_REPORT :
		QMI_LOC_EVENT_REGISTRATION_FLAG_NMEA, NULL);
	qmi_client_loc_register_events (
		session->client, input, 20, session->cancellable,
		(GAsyncReadyCallback) register_events_ready, session);
	qmi_message_loc_register_events_input_unref (input);
}

static void
set_nmea_ready (QmiClientLoc *client, GAsyncResult *result, gpointer user_data)
{
	struct session *session = user_data;
	QmiMessageLocSetNmeaTypesOutput *output;
	GError *error = NULL;

	output = qmi_client_loc_set_nmea_types_finish (client, result, &error);
	if (!output) {
		print_error ("set-nmea", error);
		g_clear_error (&error);
		finish (session, 1);
		return;
	}
	if (!qmi_message_loc_set_nmea_types_output_get_result (output, &error)) {
		if (!nmea_types_error_is_optional (error)) {
			print_error ("set-nmea-result", error);
			g_clear_error (&error);
			qmi_message_loc_set_nmea_types_output_unref (output);
			finish (session, 1);
			return;
		}
		/* Some LOC implementations reject this optional configuration.
		 * Keep their default sentence selection, but still require real
		 * NMEA fixes and a successful start/stop for acceptance. */
		g_print ("LOCATION_SESSION_NMEA_DEFAULTS reason=not-supported\n");
		g_clear_error (&error);
	}
	qmi_message_loc_set_nmea_types_output_unref (output);

	register_events (session);
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
	g_signal_connect (session->client, "position-report",
			  G_CALLBACK (position_received), session);
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
	GList *nodes, *services;
	GError *error = NULL;

	(void)source;
	bus = qrtr_bus_new_finish (result, &error);
	if (!bus) {
		print_error ("open-qrtr", error);
		g_clear_error (&error);
		finish (session, 1);
		return;
	}
	/* Enumerate the actual LOC endpoints before selecting the existing node.
	 * libqmi's QRTR backend selects the highest-version service port. Keep
	 * this evidence so a rejected mask is not diagnosed by guessing a node. */
	for (nodes = qrtr_bus_peek_nodes (bus); nodes; nodes = nodes->next) {
		QrtrNode *candidate = QRTR_NODE (nodes->data);
		for (services = qrtr_node_peek_service_info_list (candidate);
		     services; services = services->next) {
			QrtrNodeServiceInfo *info = services->data;
			if (qrtr_node_service_info_get_service (info) == QMI_SERVICE_LOC)
				g_print ("LOCATION_SESSION_LOC_SERVICE node=%u port=%u version=%u instance=%u selected_snapshot=%u\n",
					 qrtr_node_get_id (candidate),
					 qrtr_node_service_info_get_port (info),
					 qrtr_node_service_info_get_version (info),
					 qrtr_node_service_info_get_instance (info),
					 qrtr_node_get_id (candidate) == 0 &&
					 qrtr_node_lookup_port (candidate, QMI_SERVICE_LOC) ==
					 (gint32) qrtr_node_service_info_get_port (info));
		}
	}
	fflush (stdout);
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
	session->terminate_requested = TRUE;
	if (session->stop_requested)
		return G_SOURCE_REMOVE;
	/* Let the bounded start callback settle before sending stop. This avoids
	 * accepting stop while a later start acknowledgement is still pending. */
	if (session->start_pending)
		return G_SOURCE_REMOVE;
	if (session->client && session->start_requested && !session->stopped)
		request_stop (session);
	else
		finish (session, 1);
	return G_SOURCE_REMOVE;
}

static gboolean
unix_terminate (gpointer user_data)
{
	terminate (user_data);
	/* Keep the handler installed so a repeated SIGTERM cannot interrupt
	 * an in-flight LOC stop by reverting to the default signal action. */
	return G_SOURCE_CONTINUE;
}

static gboolean
deadline_expired (gpointer user_data)
{
	struct session *session = user_data;
	session->deadline_id = 0;
	return terminate (session);
}

int
main (int argc, char **argv)
{
	struct session session = { 0 };
	unsigned int seconds = 45;

	if (argc == 2 && g_str_equal (argv[1], "--self-test"))
		return configuration_self_test ();
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
	g_unix_signal_add (SIGINT, unix_terminate, &session);
	g_unix_signal_add (SIGTERM, unix_terminate, &session);
	/* Allow pending start (20s) and stop (20s) after this soft deadline.
	 * The Python wrapper reserves 95 seconds beyond collection time. */
	session.deadline_id =
		g_timeout_add_seconds (seconds + 45, deadline_expired, &session);
	qrtr_bus_new (5000, session.cancellable,
		      (GAsyncReadyCallback) bus_ready, &session);
	g_main_loop_run (session.loop);
	if (!session.start_requested)
		g_print ("LOCATION_SESSION_NO_SESSION start_requested=0\n");

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
