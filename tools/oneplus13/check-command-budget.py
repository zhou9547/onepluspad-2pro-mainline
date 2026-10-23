#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Execute actual DPU budget/check/ICC functions; never measures frame timing."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kernel-source', required=True, type=Path)
    parser.add_argument('--patched-source', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    pin = json.loads((repo/'devices/oneplus13/source.json').read_text())['kernel']['commit']
    if subprocess.check_output(['git', '-C', str(args.kernel_source), 'rev-parse', 'HEAD'], text=True).strip() != pin:
        raise ValueError('Kernel pin mismatch')
    path = 'drivers/gpu/drm/msm/disp/dpu1/dpu_core_perf.c'
    source = ((args.patched_source or args.kernel_source)/path).read_text()
    baseline = subprocess.check_output(['git', '-C', str(args.kernel_source), 'show', pin+':'+path], text=True)
    spec = importlib.util.spec_from_file_location('display_check', Path(__file__).with_name('check-display.py'))
    check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(check)
    extract = check.extract_function
    signatures = ['static int dpu_aa569_spr_scale(', 'static int dpu_aa569_spr_budget(',
                  'int dpu_core_perf_crtc_check(', 'static int _dpu_core_perf_crtc_update_bus(']
    functions = '\n'.join(extract(source, s) for s in signatures)
    for signature, name, new_name in [(signatures[2], 'dpu_core_perf_crtc_check', 'baseline_check'),
                                      (signatures[3], '_dpu_core_perf_crtc_update_bus', 'baseline_bus')]:
        functions += '\n'+extract(baseline, signature).replace(name+'(', new_name+'(', 1)
    prefix = r'''
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
typedef uint64_t u64;typedef uint32_t u32;
#define U32_MAX UINT32_MAX
#define EINVAL 22
#define E2BIG 7
#define ENODEV 19
#define EOVERFLOW 75
#define check_mul_overflow(a,b,out) __builtin_mul_overflow(a,b,out)
#define max(a,b) ((a)>(b)?(a):(b))
#define DIV_ROUND_UP_ULL(a,b) (((a)+(b)-1)/(b))
#define DPU_ERROR(...) ((void)0)
#define DRM_DEBUG_ATOMIC(...) ((void)0)
#define CHECK(x) do{if(!(x)){fprintf(stderr,"Budget check failed at %d\n",__LINE__);exit(1);}}while(0)
enum {DPU_PERF_MODE_NORMAL,DPU_PERF_MODE_MINIMUM,DPU_PERF_MODE_FIXED};
enum {RT_CLIENT,NRT_CLIENT};
struct dpu_core_perf_params {u32 max_per_pipe_ib;u64 bw_ctl,core_clk_rate;};
struct dpu_perf_cfg {u32 max_bw_high;};
struct dpu_core_perf {struct dpu_perf_cfg *perf_cfg;u64 max_opp_clk_rate;struct {u32 mode;}perf_tune;u32 fix_core_ab_vote,fix_core_ib_vote;};
struct dpu_kms {void *aa569_spr;int num_paths,path[4];struct dpu_core_perf perf;};
struct drm_crtc_state {bool enable;};
struct dpu_crtc_state {struct drm_crtc_state base;struct dpu_core_perf_params new_perf;};
struct drm_crtc {void *dev;};
static struct dpu_kms kms;
static struct dpu_core_perf_params input, aggregate;
static unsigned icc_calls;static int icc_error_at=-1;static u32 icc_avg[4],icc_peak[4];
static u64 div_u64_rem(u64 v,u32 d,u32*r){*r=v%d;return v/d;}
static u64 div_u64(u64 v,u32 d){return v/d;}
static struct dpu_kms *_dpu_crtc_get_kms(struct drm_crtc*c){(void)c;return &kms;}
static int dpu_crtc_get_client_type(struct drm_crtc*c){(void)c;return RT_CLIENT;}
#define to_dpu_crtc_state(p) ((struct dpu_crtc_state *)(p))
static void _dpu_core_perf_calc_crtc(struct dpu_core_perf*p,struct drm_crtc*c,struct drm_crtc_state*s,struct dpu_core_perf_params*out){(void)p;(void)c;(void)s;*out=input;}
/* Deliberately expose an old zero state: the new enabled state must be checked
 * directly, without assuming that the generic aggregator already sees it. */
static void dpu_core_perf_aggregate(void*d,int t,struct dpu_core_perf_params*out){(void)d;(void)t;*out=aggregate;}
static int icc_set_bw(int path,u32 avg,u32 peak){unsigned n=icc_calls++;(void)path;icc_avg[n]=avg;icc_peak[n]=peak;return (int)n==icc_error_at?-5:0;}
'''
    rng = random.Random(6800)
    cases = [(0, 0, 0), (1, 1, 1), (102, 102, 102), (103, 103, 103),
             (2211840000, 580608000, 800000)]
    cases += [(rng.randrange(1, 10_000_000_000), rng.randrange(1, 600_000_000),
               rng.randrange(1, 2_000_000)) for _ in range(256)]
    fixture = 'static const u64 vectors[][6]={\n'
    for bw, clock, peak in cases:
        scaled = lambda n: (n*125+101)//102
        values = [bw, clock, peak, scaled(bw), scaled(clock), max(scaled(peak), (scaled(bw)+999)//1000)]
        fixture += '{'+','.join(str(n)+'ULL' for n in values)+'},\n'
    fixture += '};\n'
    suffix = r'''
int main(void){
 struct dpu_perf_cfg cfg={28500000};struct drm_crtc crtc={0};struct dpu_crtc_state state={.base.enable=true};
 kms.perf.perf_cfg=&cfg;kms.perf.max_opp_clk_rate=1000000000;kms.num_paths=2;
 for(unsigned i=0;i<sizeof(vectors)/sizeof(vectors[0]);i++){
  const u64*v=vectors[i];struct dpu_core_perf_params p={.bw_ctl=v[0],.core_clk_rate=v[1],.max_per_pipe_ib=v[2]};
  CHECK(!dpu_aa569_spr_budget(&p,1000000000));
  CHECK(p.bw_ctl==v[3]&&p.core_clk_rate==v[4]&&p.max_per_pipe_ib==v[5]);
 }
 for(int i=0;i<5;i++){
  struct dpu_core_perf_params p={.bw_ctl=2000000000,.core_clk_rate=580608000,.max_per_pipe_ib=800000};
  u64 limit=1000000000;
  if(i==0)p.bw_ctl=UINT64_MAX;
  if(i==1)p.core_clk_rate=UINT64_MAX;
  if(i==2)p.max_per_pipe_ib=UINT32_MAX;
  if(i==3)limit=600000000;
  if(i==4)limit=0;
  struct dpu_core_perf_params saved=p;CHECK(dpu_aa569_spr_budget(&p,limit)<0);CHECK(!memcmp(&p,&saved,sizeof(p)));
 }
 input=(struct dpu_core_perf_params){.bw_ctl=2211840000,.core_clk_rate=580608000,.max_per_pipe_ib=800000};
 kms.aa569_spr=&kms;
 CHECK(!dpu_core_perf_crtc_check(&crtc,&state.base));
 CHECK(state.new_perf.core_clk_rate==711529412&&state.new_perf.bw_ctl==2710588236ULL);
 /* A fresh enable has an empty old aggregate. Still reject the NEW limits. */
 kms.perf.max_opp_clk_rate=600000000;
 CHECK(dpu_core_perf_crtc_check(&crtc,&state.base)==-E2BIG);
 CHECK(!baseline_check(&crtc,&state.base));
 kms.perf.max_opp_clk_rate=1000000000;cfg.max_bw_high=2500000;
 CHECK(dpu_core_perf_crtc_check(&crtc,&state.base)==-E2BIG);CHECK(!baseline_check(&crtc,&state.base));
 cfg.max_bw_high=28500000;
 for(int mode=1;mode<=2;mode++){kms.perf.perf_tune.mode=mode;CHECK(dpu_core_perf_crtc_check(&crtc,&state.base)==-EINVAL);}
 kms.perf.perf_tune.mode=0;kms.aa569_spr=NULL;
 for(int mode=0;mode<=2;mode++){
  kms.perf.perf_tune.mode=mode;
  CHECK(!dpu_core_perf_crtc_check(&crtc,&state.base));struct dpu_core_perf_params current=state.new_perf;
  CHECK(!baseline_check(&crtc,&state.base));CHECK(!memcmp(&current,&state.new_perf,sizeof(current)));
 }
 kms.perf.perf_tune.mode=0;kms.aa569_spr=&kms;
 CHECK(!dpu_core_perf_crtc_check(&crtc,&state.base));aggregate=state.new_perf;
 for(int fail=0;fail<2;fail++){
  icc_calls=0;icc_error_at=fail;CHECK(_dpu_core_perf_crtc_update_bus(&kms,&crtc)==-5);CHECK(icc_calls==(unsigned)fail+1);
 }
 icc_calls=0;icc_error_at=-1;CHECK(!_dpu_core_perf_crtc_update_bus(&kms,&crtc));
 CHECK(icc_calls==2&&icc_avg[0]==1355295&&icc_avg[1]==1355295&&icc_peak[0]==2710589);
 kms.num_paths=0;CHECK(_dpu_core_perf_crtc_update_bus(&kms,&crtc)==-ENODEV);
 kms.aa569_spr=NULL;CHECK(!_dpu_core_perf_crtc_update_bus(&kms,&crtc));kms.num_paths=2;
 for(int mode=0;mode<=2;mode++){
  kms.perf.perf_tune.mode=mode;icc_calls=0;icc_error_at=0;CHECK(!_dpu_core_perf_crtc_update_bus(&kms,&crtc));
  u32 a=icc_avg[0],p=icc_peak[0];icc_calls=0;CHECK(!baseline_bus(&kms,&crtc));CHECK(a==icc_avg[0]&&p==icc_peak[0]);
 }
 puts("AA569 budget vectors, fresh-state/OPP limits, ICC errors and legacy controls passed");
 return 0;
}
'''
    with tempfile.TemporaryDirectory(prefix='oneplus13-budget-') as tmp:
        c, exe = Path(tmp)/'budget.c', Path(tmp)/'budget.exe'
        c.write_text(prefix+functions+fixture+suffix)
        command = ['gcc', '-std=gnu11', '-Wall', '-Wextra', '-Werror']
        if args.sanitize:
            command += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        subprocess.run(command+[str(c), '-o', str(exe)], check=True)
        subprocess.run([str(exe)], check=True)
    report = {'scope': 'HOST_C_DPU_COMMAND_BUDGET_ONLY', 'hardware_tested': False,
              'kernel_commit': pin, 'sanitizers': args.sanitize,
              'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
              'nominal_refresh_hz': 120, 'stock_budget_us': 6800,
              'ceiling_multiplier': [125, 102], 'arithmetic_vectors': len(cases),
              'overflow_peak_opp_zero_limit_rejected': 5,
              'fresh_enable_new_state_limits_checked': True, 'baseline_underbudget_rejected': True,
              'nonoptin_legacy_modes_unchanged': 3, 'icc_error_positions': 2,
              'icc_per_path_average_ceiling': True, 'missing_icc_path_rejected': True,
              'te_timing_changed': False, 'hardware_transfer_timer_programmed': False,
              'exact_vendor_hal_algorithm': False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
