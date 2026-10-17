#!/usr/bin/env python3
"""跨 profile / 共享根 技能重复扫描：三类分类报告。
用法: python3 skill_diff_scan.py
输出: /tmp/skill_diff_report.json + 控制台摘要
判定: 目录指纹 = 全部文件(relpath:sha1)组合 sha1
  IDENTICAL_to_shared      — profile 副本与共享根完全一致 → 可删副本
  ***SECRET*** — 共享根没有但各 profile 间一致 → 提升正本后删全部
  DIFFERENT_from_shared    — 不一致 → 逐个看差异归属（超集/互有扩展）
  PROFILE_ONLY             — 单 profile 独有 → 不动
"""
import os, hashlib, json
from collections import defaultdict

PROFILES = ["afu","community","default","heidou","laomo","maodou","psychology","quant","test","xiaobao","zhenglishi"]
BASE = "/Users/hua/.hermes/profiles"

def skill_fingerprint(skill_dir):
    files = []
    for dp, dn, fn in os.walk(skill_dir):
        dn[:] = [d for d in dn if d not in (".git","node_modules","__pycache__")]
        for f in fn:
            p = os.path.join(dp, f)
            files.append((os.path.relpath(p, skill_dir), hashlib.sha1(open(p,'rb').read()).hexdigest()))
    combined = hashlib.sha1("|".join(f"{k}:{v}" for k,v in sorted(files)).encode()).hexdigest()
    total = sum(os.path.getsize(os.path.join(dp,f)) for dp,_,fs in os.walk(skill_dir) for f in fs)
    return combined, len(files), total

def main():
    per_profile = {}
    for p in PROFILES:
        sd = os.path.join(BASE, p, "skills")
        if not os.path.isdir(sd): continue
        per_profile[p] = {n: os.path.join(sd, n) for n in sorted(os.listdir(sd))
                          if os.path.isdir(os.path.join(sd, n)) and os.path.exists(os.path.join(sd, n, "SKILL.md"))}
    shared = {}
    sroot = "/Users/hua/.hermes/skills"
    for dirpath, dirnames, filenames in os.walk(sroot):
        if "/.archive" in dirpath:
            dirnames[:] = [d for d in dirnames if d != ".archive"]; continue
        if "SKILL.md" in filenames:
            rel = os.path.relpath(dirpath, sroot)
            if rel.count(os.sep) <= 1 and rel not in shared:
                shared[rel] = dirpath
    name_map = defaultdict(dict)
    for p, m in per_profile.items():
        for name, path in m.items(): name_map[name][p] = path
    report = {"IDENTICAL_to_shared":[], "DIFFERENT_from_shared":[], "***SECRET***":[], "PROFILE_ONLY_count":0}
    for name, holders in sorted(name_map.items()):
        if len(holders) < 2 and name not in shared:
            report["PROFILE_ONLY_count"] += 1; continue
        sh_path = shared.get(name)
        sh_fp = skill_fingerprint(sh_path) if sh_path else None
        fps = {p: skill_fingerprint(path) for p, path in holders.items()}
        if sh_fp:
            same = [p for p,fp in fps.items() if fp[0]==sh_fp[0]]
            diff = [p for p,fp in fps.items() if fp[0]!=sh_fp[0]]
            if not diff:
                report["IDENTICAL_to_shared"].append({"name":name,"profiles":sorted(fps),"files":sh_fp[1],"kb":sh_fp[2]//1024})
            else:
                report["DIFFERENT_from_shared"].append({"name":name,"same_profiles":sorted(same),"diff_profiles":sorted(diff),
                    "detail":{p:{"files":fps[p][1],"kb":fps[p][2]//1024} for p in sorted(fps)},
                    "shared":{"files":sh_fp[1],"kb":sh_fp[2]//1024}})
        else:
            if len(set(fp[0] for fp in fps.values()))==1 and len(holders)>=2:
                v = list(fps.values())[0]
                report["***SECRET***"].append({"name":name,"profiles":sorted(fps),"files":v[1],"kb":v[2]//1024})
            else:
                report["DIFFERENT_from_shared"].append({"name":name,"same_profiles":None,"diff_profiles":sorted(fps),
                    "detail":{p:{"files":fps[p][1],"kb":fps[p][2]//1024} for p in sorted(fps)},"shared":None})
    json.dump(report, open("/tmp/skill_diff_report.json","w"), ensure_ascii=False, indent=1)
    print({k: (len(v) if isinstance(v, list) else v) for k,v in report.items()})
    print("IDENTICAL 可回收 ~%dMB" % (sum(x["kb"] for x in report["IDENTICAL_to_shared"])//1024))

if __name__ == "__main__":
    main()
