#!/bin/sh
# docs/app/* 를 gh-pages 브랜치 루트로 배포한다.
# 사용: web/deploy.sh "커밋 메시지"
# 컨테이너가 재시작돼도 되도록 저장소 안에 둔다. 별도 클론에 의존하지 않는다
set -e
cd "$(dirname "$0")/.."
python3 web/build.py
WT=$(mktemp -d)
git fetch -q origin gh-pages
git worktree add -q -f --detach "$WT" FETCH_HEAD
rm -rf "$WT"/*.html "$WT"/*.png "$WT"/*.webmanifest "$WT"/*.js "$WT"/voice "$WT"/sounds
cp -R docs/app/. "$WT"/
touch "$WT/.nojekyll"
git -C "$WT" add -A
if git -C "$WT" diff --cached --quiet; then
  echo "배포할 변경 없음"
else
  git -C "$WT" -c user.name=Claude -c user.email=noreply@anthropic.com commit -q -m "${1:-pages: 배포}"
  git -C "$WT" push -q origin HEAD:gh-pages
  echo "배포 완료: $(git -C "$WT" rev-parse --short HEAD)"
fi
git worktree remove --force "$WT"
