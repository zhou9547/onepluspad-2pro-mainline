// SPDX-License-Identifier: GPL-2.0-only
/*
 * OnePlus 13 AA569 P3 A0019 component; not a complete display pipeline.
 * Public packets: OnePlusOSS d50b305f7da9; generated header retains all bytes.
 * No DTB enables this component until DPU SPR2/lifecycle is implemented.
 * Author: Codex. No hardware Tested-by claim.
 */
#include <linux/delay.h>
#include <linux/gpio/consumer.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/of.h>
#include <linux/regulator/consumer.h>
#include <linux/slab.h>
#include <drm/display/drm_dsc.h>
#include <drm/drm_connector.h>
#include <drm/drm_mipi_dsi.h>
#include <drm/drm_modes.h>
#include <drm/drm_panel.h>
#include "aa569-data.h"

struct aa569 {
	struct drm_panel panel;
	struct mipi_dsi_device *dsi;
	struct regulator *vddio, *vci;
	struct gpio_desc *reset, *vddr;
	struct mutex lock;
	struct drm_dsc_config dsc;
	bool vddio_on, vci_on, vddr_on, prepared, enabled;
};

static struct aa569 *to_aa569(struct drm_panel *panel)
{
	return container_of(panel, struct aa569, panel);
}

static int aa569_send(struct aa569 *ctx, const struct aa569_cmd *cmd,
		      const u8 *bytes, size_t count, bool lp)
{
	unsigned long flags = ctx->dsi->mode_flags;
	ssize_t ret = 0;
	size_t i;

	/* Vendor 0x40 groups host DMA packets; it is not a panel payload flag.
	 * Mainline sends them serially, retaining byte/type/channel/order/delay.
	 * Only this driver changes the device flags, under ctx->lock.
	 */
	ctx->dsi->mode_flags &= ~MIPI_DSI_MODE_LPM;
	if (lp)
		ctx->dsi->mode_flags |= MIPI_DSI_MODE_LPM;
	for (i = 0; i < count; i++) {
		ret = mipi_dsi_dcs_write_buffer(ctx->dsi, bytes + cmd[i].offset,
					      cmd[i].length);
		if (ret < 0)
			break;
		if (ret != cmd[i].length) {
			ret = -EIO;
			break;
		}
		if (cmd[i].delay_ms)
			msleep(cmd[i].delay_ms);
	}
	ctx->dsi->mode_flags = flags;
	return ret < 0 ? ret : 0;
}

static int aa569_power_off(struct aa569 *ctx)
{
	int ret;

	gpiod_set_value_cansleep(ctx->reset, 1); /* active-low RESET asserted */
	msleep(1);
	if (ctx->vci_on) {
		ret = regulator_disable(ctx->vci);
		if (ret)
			return ret; /* keep upstream rails if VCI did not turn off */
		ctx->vci_on = false;
		ret = regulator_set_load(ctx->vci, 300);
		if (ret < 0)
			dev_warn(&ctx->dsi->dev, "VCI off load: %d\n", ret);
	}
	msleep(3);
	if (ctx->vddr_on) {
		gpiod_set_value_cansleep(ctx->vddr, 0);
		ctx->vddr_on = false;
	}
	msleep(3);
	if (ctx->vddio_on) {
		ret = regulator_disable(ctx->vddio);
		if (ret)
			return ret;
		ctx->vddio_on = false;
		ret = regulator_set_load(ctx->vddio, 8000);
		if (ret < 0)
			dev_warn(&ctx->dsi->dev, "VDDIO off load: %d\n", ret);
	}
	msleep(1);
	return 0;
}

static int aa569_power_on(struct aa569 *ctx)
{
	int ret, cleanup;

	if (ctx->vci_on || ctx->vddr_on || ctx->vddio_on)
		return -EBUSY; /* failed teardown must be retried before another enable */
	msleep(1);
	ret = regulator_set_load(ctx->vddio, 220000);
	if (ret < 0)
		return ret;
	ret = regulator_enable(ctx->vddio);
	if (ret)
		goto fail;
	ctx->vddio_on = true;
	msleep(3);
	gpiod_set_value_cansleep(ctx->vddr, 1);
	ctx->vddr_on = true;
	msleep(3);
	ret = regulator_set_load(ctx->vci, 10000);
	if (ret < 0)
		goto fail;
	ret = regulator_enable(ctx->vci);
	if (ret)
		goto fail;
	ctx->vci_on = true;
	msleep(10);
	/* Logical 0 is physical HIGH for the required active-low reset GPIO. */
	gpiod_set_value_cansleep(ctx->reset, 0);
	msleep(10);
	gpiod_set_value_cansleep(ctx->reset, 1);
	msleep(5);
	gpiod_set_value_cansleep(ctx->reset, 0);
	msleep(30);
	return 0;
fail:
	cleanup = aa569_power_off(ctx);
	if (cleanup)
		dev_err(&ctx->dsi->dev, "power rollback failed: %d\n", cleanup);
	/* A failed enable still leaves a requested load on the disabled supply. */
	if (!ctx->vci_on)
		regulator_set_load(ctx->vci, 300);
	if (!ctx->vddio_on)
		regulator_set_load(ctx->vddio, 8000);
	return ret;
}

static int aa569_prepare(struct drm_panel *panel)
{
	struct aa569 *ctx = to_aa569(panel);
	int ret;

	mutex_lock(&ctx->lock);
	if (ctx->prepared) {
		ret = 0;
		goto out;
	}
	ret = aa569_power_on(ctx);
	if (ret)
		goto out;
	/* Last packet is display-on; defer that packet to the enable callback. */
	ret = aa569_send(ctx, aa569_on, aa569_on_bytes, ARRAY_SIZE(aa569_on) - 1, true);
	if (ret) {
		int cleanup = aa569_power_off(ctx);

		if (cleanup)
			dev_err(&ctx->dsi->dev, "prepare rollback failed: %d\n", cleanup);
		goto out;
	}
	ctx->prepared = true;
out:
	mutex_unlock(&ctx->lock);
	return ret;
}

static int aa569_enable(struct drm_panel *panel)
{
	struct aa569 *ctx = to_aa569(panel);
	/* Fixed normal-range starting DBV1433, MSB first as in inverted stock
	 * callback. No HBM, PWM switching, low-DBV, AOD or brightness UI yet.
	 */
	static const u8 brightness[] = { 0x51, 0x05, 0x99 };
	static const struct aa569_cmd bright_cmd = { 0, sizeof(brightness), 0 };
	int ret;

	mutex_lock(&ctx->lock);
	if (!ctx->prepared) {
		ret = -EPERM;
		goto out;
	}
	if (ctx->enabled) {
		ret = 0;
		goto out;
	}
	ret = aa569_send(ctx, aa569_on + ARRAY_SIZE(aa569_on) - 1,
			 aa569_on_bytes, 1, true);
	if (ret)
		goto out;
	ret = aa569_send(ctx, &bright_cmd, brightness, 1, false);
	if (ret) {
		/* The display-on packet succeeded. Disable must still send sleep-in. */
		ctx->enabled = true;
		goto out;
	}
	ctx->enabled = true;
out:
	mutex_unlock(&ctx->lock);
	return ret;
}

static int aa569_disable_locked(struct aa569 *ctx)
{
	int ret;

	if (!ctx->prepared || !ctx->enabled)
		return 0;
	/* Leave the panel awake for a possible disable/enable without unprepare. */
	ret = aa569_send(ctx, aa569_off, aa569_off_bytes, ARRAY_SIZE(aa569_off) - 1, false);
	if (!ret)
		ctx->enabled = false;
	return ret;
}

static int aa569_disable(struct drm_panel *panel)
{
	struct aa569 *ctx = to_aa569(panel);
	int ret;

	mutex_lock(&ctx->lock);
	ret = aa569_disable_locked(ctx);
	mutex_unlock(&ctx->lock);
	return ret;
}

static int aa569_unprepare(struct drm_panel *panel)
{
	struct aa569 *ctx = to_aa569(panel);
	int ret, first = 0;

	mutex_lock(&ctx->lock);
	if (ctx->enabled)
		first = aa569_disable_locked(ctx);
	if (ctx->prepared) {
		ret = aa569_send(ctx, aa569_off + ARRAY_SIZE(aa569_off) - 1,
				 aa569_off_bytes, 1, false);
		if (!first)
			first = ret;
	}
	ret = aa569_power_off(ctx); /* also retries incomplete prepare rollback */
	if (!ret) {
		ctx->prepared = false;
		ctx->enabled = false;
	}
	mutex_unlock(&ctx->lock);
	return first ?: ret;
}

static const struct drm_display_mode aa569_mode = {
	.clock = 599808,
	.hdisplay = 1440, .hsync_start = 1504, .hsync_end = 1512, .htotal = 1562,
	.vdisplay = 3168, .vsync_start = 3184, .vsync_end = 3188, .vtotal = 3200,
	.width_mm = 71, .height_mm = 158,
	.type = DRM_MODE_TYPE_DRIVER | DRM_MODE_TYPE_PREFERRED,
};

static int aa569_get_modes(struct drm_panel *panel, struct drm_connector *connector)
{
	struct drm_display_mode *mode = drm_mode_duplicate(connector->dev, &aa569_mode);

	if (!mode)
		return -ENOMEM;
	drm_mode_set_name(mode);
	drm_mode_probed_add(connector, mode);
	connector->display_info.width_mm = aa569_mode.width_mm;
	connector->display_info.height_mm = aa569_mode.height_mm;
	connector->display_info.bpc = 10;
	return 1;
}

static const struct drm_panel_funcs aa569_funcs = {
	.prepare = aa569_prepare, .enable = aa569_enable, .disable = aa569_disable,
	.unprepare = aa569_unprepare, .get_modes = aa569_get_modes,
};

static int aa569_probe(struct mipi_dsi_device *dsi)
{
	struct device *dev = &dsi->dev;
	struct aa569 *ctx;
	int ret;

	ctx = devm_kzalloc(dev, sizeof(*ctx), GFP_KERNEL);
	if (!ctx)
		return -ENOMEM;
	ctx->dsi = dsi;
	mutex_init(&ctx->lock);
	ctx->vddio = devm_regulator_get(dev, "vddio");
	if (IS_ERR(ctx->vddio))
		return dev_err_probe(dev, PTR_ERR(ctx->vddio), "VDDIO supply\n");
	ctx->vci = devm_regulator_get(dev, "vci");
	if (IS_ERR(ctx->vci))
		return dev_err_probe(dev, PTR_ERR(ctx->vci), "VCI supply\n");
	/* DTS must constrain VDDIO to1.8V and VCI to3.0V. */
	ctx->reset = devm_gpiod_get(dev, "reset", GPIOD_ASIS);
	if (IS_ERR(ctx->reset))
		return dev_err_probe(dev, PTR_ERR(ctx->reset), "RESET GPIO\n");
	ctx->vddr = devm_gpiod_get(dev, "vddr", GPIOD_ASIS);
	if (IS_ERR(ctx->vddr))
		return dev_err_probe(dev, PTR_ERR(ctx->vddr), "VDDR GPIO\n");
	if (!gpiod_is_active_low(ctx->reset) || gpiod_is_active_low(ctx->vddr))
		return dev_err_probe(dev, -EINVAL, "Incorrect GPIO polarity\n");
	ret = gpiod_direction_output(ctx->reset, 1);
	if (ret)
		return dev_err_probe(dev, ret, "RESET direction\n");
	ret = gpiod_direction_output(ctx->vddr, 0);
	if (ret)
		return dev_err_probe(dev, ret, "VDDR direction\n");
	drm_panel_init(&ctx->panel, dev, &aa569_funcs, DRM_MODE_CONNECTOR_DSI);
	ctx->panel.prepare_prev_first = true;
	ctx->dsc = aa569_dsc;
	dsi->dsc = &ctx->dsc;
	dsi->dsc_slice_per_pkt = 2;
	dsi->lanes = 4;
	dsi->format = MIPI_DSI_FMT_RGB101010;
	dsi->mode_flags = MIPI_DSI_MODE_NO_EOT_PACKET | MIPI_DSI_CLOCK_NON_CONTINUOUS;
	dsi->hs_rate = 1363200000;
	mipi_dsi_set_drvdata(dsi, ctx);
	drm_panel_add(&ctx->panel);
	ret = mipi_dsi_attach(dsi);
	if (ret)
		drm_panel_remove(&ctx->panel);
	return ret;
}

static void aa569_remove(struct mipi_dsi_device *dsi)
{
	struct aa569 *ctx = mipi_dsi_get_drvdata(dsi);
	int ret;

	ret = aa569_unprepare(&ctx->panel);
	if (ret)
		dev_err(&dsi->dev, "teardown failed: %d\n", ret);
	mipi_dsi_detach(dsi);
	drm_panel_remove(&ctx->panel);
}

static void aa569_shutdown(struct mipi_dsi_device *dsi)
{
	struct aa569 *ctx = mipi_dsi_get_drvdata(dsi);
	int ret = aa569_unprepare(&ctx->panel);

	if (ret)
		dev_err(&dsi->dev, "shutdown failed: %d\n", ret);
}

static const struct of_device_id aa569_of_match[] = {
	{ .compatible = "oneplus,dodge-aa569" }, { }
};
MODULE_DEVICE_TABLE(of, aa569_of_match);

static struct mipi_dsi_driver aa569_driver = {
	.probe = aa569_probe, .remove = aa569_remove, .shutdown = aa569_shutdown,
	.driver = { .name = "panel-oneplus-aa569", .of_match_table = aa569_of_match },
};
module_mipi_dsi_driver(aa569_driver);
MODULE_AUTHOR("Codex");
MODULE_DESCRIPTION("Experimental AA569 panel component; DPU SPR2 integration required");
MODULE_LICENSE("GPL");
