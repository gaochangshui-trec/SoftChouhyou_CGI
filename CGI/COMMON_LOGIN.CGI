#!/bin/bash -xv
#
# COMMON_LOGIN.CGI >>> MDPLANログイン
# Usage : COMMON_LOGIN.CGI
#
# Written by Chou.Shin(TRE・CHINA) / Date : 22 Aug. 2016

#/////////////////////////////////////////////////////////////////////////
# 初期設定
#/////////////////////////////////////////////////////////////////////////

# 環境変数設定
export PATH=/home/SMART:/home/SMART_TRIAL:/usr/local/bin:${PATH}
export LANG=ja_JP.UTF-8

## ログディレクトリの定義
logd=/home/trial/AP/SOFT_CHOUHYOU/LOG

##走行ログの記録
echo "${logd}/LOG.$(basename $0).$(date +%Y%m%d)_$(date +%H%M%S)_$$" &>/dev/null
exec 2>${logd}/LOG.$(basename $0).$(date +%Y%m%d)_$(date +%H%M%S)_$$

# ディレクトリ定義
tmp=/tmp/$$-$(basename $0)_$(date +%Y%m%d)_$(date +%H%M%S)

dir=/home/trial
shld=${dir}/AP/SOFT_CHOUHYOU/CGI

echo "Content-Type:text;charset=UTF-8"
echo ""

# エラー時の終了処理定義
ERROR_EXIT(){
  echo '{"error":"1"}'
  exit 1
}

#画面から入力のデータ取得
dd count=$CONTENT_LENGTH bs=1 |
qsstr -l_ -i_                 > $tmp-param
[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT

# 登録者
usercd=$(readvalue -uUSERCD $tmp-param)
[ -z ${usercd} ] && ERROR_EXIT

# 登録パスワード
password=$(readvalue -uPASSWORD $tmp-param)
[ -z ${password} ] && ERROR_EXIT

shl=COMMON_LOGIN.CHECK
${shld}/${shl} ${usercd} ${password} > $tmp-result
[ $? -eq 0 ] || ERROR_EXIT

if [ $(cat $tmp-result) -eq 1 ] ; then
  echo '{"error":"0"}'
  [ $? -eq 0 ] || ERROR_EXIT
else
  echo '{"error":"1"}'
  [ $? -eq 0 ] || ERROR_EXIT
fi

#/////////////////////////////////////////////////////////////////////////
# 終了部分
#/////////////////////////////////////////////////////////////////////////
# 終了
rm -rf $tmp* &> /dev/null
exit 0
