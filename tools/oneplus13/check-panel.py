#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile real AA569 component callbacks with host-only, fault-injected I/O."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--kernel-source', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--sanitize', action='store_true')
    p.add_argument('--keep-source', type=Path)
    a = p.parse_args()
    repo = Path(__file__).resolve().parents[2]
    fixture = json.loads((repo/'devices/oneplus13/panel-aa569-120hz.json').read_text())
    panel_dir = repo/'devices/oneplus13/kernel/panel-aa569'
    source = (panel_dir/'panel-oneplus-aa569.c').read_text()
    generated = load('panel_generator', Path(__file__).with_name('generate-panel.py')).generate(fixture)
    if (panel_dir/'aa569-data.h').read_text() != generated:
        raise ValueError('Generated public AA569 header is stale')
    pin = json.loads((repo/'devices/oneplus13/source.json').read_text())['kernel']['commit']
    if subprocess.check_output(['git', '-C', str(a.kernel_source), 'rev-parse', 'HEAD'], text=True).strip() != pin:
        raise ValueError('Kernel header source does not match pin')
    header = subprocess.check_output(['git', '-c', 'gc.auto=0', '-c', 'maintenance.auto=false',
        '-C', str(a.kernel_source), 'show', pin+':include/drm/display/drm_dsc.h']).decode()
    header = header.replace('#include <drm/display/drm_dp.h>', '')
    extract = load('display_check', Path(__file__).with_name('check-display.py')).extract_function
    callbacks = '\n'.join(extract(source, x) for x in [
        'static struct aa569 *to_aa569(', 'static int aa569_send(',
        'static int aa569_power_off(', 'static int aa569_power_on(',
        'static int aa569_prepare(', 'static int aa569_enable(',
        'static int aa569_disable_locked(', 'static int aa569_disable(',
        'static int aa569_unprepare('])
    prefix = r'''
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32; typedef uint16_t __be16;
#define __packed __attribute__((packed))
struct dp_sdp_header {u8 bytes[4];};
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define container_of(p,t,m) ((t *)((char *)(p)-offsetof(t,m)))
#define MIPI_DSI_MODE_LPM 0x800
struct drm_panel {int unused;};
struct mipi_dsi_device {unsigned long mode_flags; int dev;};
struct regulator {int id,on,load;};
struct gpio_desc {int id,value;};
struct mutex {int held;};
static void mutex_lock(struct mutex *m) {if(m->held)abort();m->held=1;}
static void mutex_unlock(struct mutex *m) {if(!m->held)abort();m->held=0;}
static int verbose,op,fail_op,tx,fail_tx,short_tx,fail_disable_id;
#define dev_warn(dev,...) do {(void)(dev);} while(0)
#define dev_err(dev,...) do {(void)(dev);} while(0)
static void msleep(unsigned int ms) {if(verbose)printf("W %u\n",ms);}
static int regulator_set_load(struct regulator *r,int load) {
 if(verbose)printf("L %d %d\n",r->id,load);
 if(++op==fail_op)return -EIO;
 r->load=load;return 0;
}
static int regulator_enable(struct regulator *r) {
 if(verbose)printf("E %d\n",r->id);
 if(++op==fail_op)return -EIO;
 if(r->on)abort();
 r->on=1;return 0;
}
static int regulator_disable(struct regulator *r) {
 if(verbose)printf("D %d\n",r->id);
 if(r->id==fail_disable_id)return -EIO;
 if(!r->on)abort();
 r->on=0;return 0;
}
static void gpiod_set_value_cansleep(struct gpio_desc *g,int value) {
 if(verbose)printf("G %d %d\n",g->id,value);
 g->value=value;
}
static ssize_t mipi_dsi_dcs_write_buffer(struct mipi_dsi_device *d,const void *p,size_t n) {
 const unsigned char *b=p;++tx;
 if(verbose){printf("P %d ",!!(d->mode_flags&MIPI_DSI_MODE_LPM));
 for(size_t i=0;i<n;i++)printf("%02x",b[i]);
 puts("");}
 if(tx==fail_tx)return -EIO;
 if(tx==short_tx)return n-1;
 return n;
}
'''
    main_c = r'''
#define CHECK(c) do {if(!(c)){fprintf(stderr,"failed at line %d\n",__LINE__);return 1;}}while(0)
static struct regulator io={.id=1},ci={.id=2};
static struct gpio_desc rst={.id=3},dr={.id=4};
static struct mipi_dsi_device dsi;
static void fresh(struct aa569 *c) {
 memset(c,0,sizeof(*c));io.on=ci.on=io.load=ci.load=0;rst.value=1;dr.value=0;
 c->dsc=aa569_dsc;
 dsi.mode_flags=0x10;c->dsi=&dsi;c->vddio=&io;c->vci=&ci;c->reset=&rst;c->vddr=&dr;
 op=tx=fail_op=fail_tx=short_tx=fail_disable_id=0;
}
static bool off(const struct aa569 *c) {
 return !c->vci_on&&!c->vddr_on&&!c->vddio_on&&!io.on&&!ci.on&&!dr.value&&rst.value==1;
}
int main(void) {
 struct aa569 c;fresh(&c);verbose=1;
 CHECK(!aa569_prepare(&c.panel)&&c.prepared&&!c.enabled&&tx==149);
 CHECK(!aa569_enable(&c.panel)&&c.enabled&&tx==151);
 CHECK(!aa569_disable(&c.panel)&&!c.enabled&&tx==153);
 CHECK(!aa569_unprepare(&c.panel)&&off(&c)&&!c.prepared&&tx==154);
 CHECK(dsi.mode_flags==0x10);verbose=0;
 /* Every init packet failure must stop I/O and unwind all enabled rails. */
 for(int i=1;i<=149;i++) {
   fresh(&c);fail_tx=i;
   CHECK(aa569_prepare(&c.panel)==-EIO && tx==i && off(&c) && !c.prepared);
   CHECK(dsi.mode_flags==0x10 && !c.lock.held);
 }
 /* Both enable failures and a short transfer still permit safe teardown. */
 for(int i=150;i<=151;i++) {
   fresh(&c);CHECK(!aa569_prepare(&c.panel));fail_tx=i;
   CHECK(aa569_enable(&c.panel)==-EIO);
   CHECK(!aa569_unprepare(&c.panel)&&off(&c)&&!c.prepared);
 }
 fresh(&c);short_tx=75;
 CHECK(aa569_prepare(&c.panel)==-EIO&&tx==75&&off(&c)&&dsi.mode_flags==0x10);
 /* Each load/enable failure before reset restores balanced supply ownership. */
 for(int i=1;i<=4;i++) {
   fresh(&c);fail_op=i;
   CHECK(aa569_prepare(&c.panel)==-EIO&&off(&c)&&!c.prepared);
 }
 /* A disable failure retains ownership and forbids a double-enable. */
 fresh(&c);CHECK(!aa569_prepare(&c.panel));fail_disable_id=2;
 CHECK(aa569_unprepare(&c.panel)==-EIO && c.vci_on && c.vddio_on && c.vddr_on);
 CHECK(aa569_power_on(&c)==-EBUSY);
 fail_disable_id=0;CHECK(!aa569_unprepare(&c.panel)&&off(&c));
 fresh(&c);CHECK(!aa569_prepare(&c.panel));fail_disable_id=1;
 CHECK(aa569_unprepare(&c.panel)==-EIO && !c.vci_on && c.vddio_on && !c.vddr_on);
 fail_disable_id=0;CHECK(!aa569_unprepare(&c.panel)&&off(&c));
 /* DPMS disable/enable without unprepare must not leave the panel asleep. */
 fresh(&c);CHECK(!aa569_prepare(&c.panel));CHECK(!aa569_enable(&c.panel));
 CHECK(!aa569_disable(&c.panel));CHECK(!aa569_enable(&c.panel));
 CHECK(tx==155);CHECK(!aa569_unprepare(&c.panel)&&off(&c));
 /* Off-command errors still reset/power down; a retry is balanced. */
 for(int i=152;i<=154;i++) {
   fresh(&c);CHECK(!aa569_prepare(&c.panel));CHECK(!aa569_enable(&c.panel));
   fail_tx=i;int first=aa569_disable(&c.panel);int last=aa569_unprepare(&c.panel);
   CHECK((first==-EIO||last==-EIO)&&off(&c)&&!c.prepared);
   CHECK(!aa569_unprepare(&c.panel)&&off(&c));
 }
 puts("OK real AA569 callbacks and fault recovery; no hardware I/O");return 0;
}
'''
    combined = prefix+header+generated+extract(source, 'struct aa569 {')+';\n'+callbacks+main_c
    with tempfile.TemporaryDirectory(prefix='oneplus13-panel-') as tmp:
        c, exe = Path(tmp)/'panel.c', Path(tmp)/'panel.exe'
        c.write_text(combined, encoding='utf-8')
        if a.keep_source:
            a.keep_source.write_text(combined, encoding='utf-8')
        command = ['gcc', '-std=gnu11', '-Wall', '-Wextra', '-Werror']
        if a.sanitize:
            command += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        subprocess.run(command+[str(c), '-o', str(exe)], check=True)
        output = subprocess.check_output([str(exe)], text=True).splitlines()
    packets = [line.split() for line in output if line.startswith('P ')]
    expected = [('1', v['payload']) for v in fixture['on_packets']]
    expected += [('0','510599')]+[('0',v['payload']) for v in fixture['off_packets']]
    if [(x[1],x[2]) for x in packets] != expected:
        raise ValueError('Actual C sender differs from public packet payload/order/LP-HS')
    power = [line for line in output if line[0] in 'WLEDG']
    expected_power = ['W 1','L 1 220000','E 1','W 3','G 4 1','W 3',
                      'L 2 10000','E 2','W 10','G 3 0','W 10','G 3 1','W 5','G 3 0','W 30',
                      'W 120','W 20','W 120','G 3 1','W 1','D 2','L 2 300','W 3',
                      'G 4 0','W 3','D 1','L 1 8000','W 1']
    if power != expected_power or not output[-1].startswith('OK '):
        raise ValueError('C power/reset/wait order differs from stock sequence')
    result = {'scope': 'HOST_C_PANEL_COMPONENT_ONLY', 'hardware_tested': False,
              'source_commit': fixture['source_commit'], 'kernel_commit': pin,
              'panel_source_sha256': hashlib.sha256(source.encode()).hexdigest(),
              'sanitizers': a.sanitize, 'public_on_packets_match': 150,
              'public_off_packets_match': 3, 'fixed_brightness_dbv': 1433,
              'on_lp_off_and_brightness_hs': True, 'power_reset_delays_match': True,
              'init_failure_positions_checked': 149, 'short_transfer_rejected': True,
              'supply_failure_controls': 6, 'disable_enable_cycle_checked': True,
              'off_command_failure_positions_checked': 3,
              'enabled_in_any_dtb': False, 'spr2_pipeline_implemented': False}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print('Real AA569 C callbacks: packets, power, reset, LP/HS and fault controls passed.')


if __name__ == '__main__':
    main()
