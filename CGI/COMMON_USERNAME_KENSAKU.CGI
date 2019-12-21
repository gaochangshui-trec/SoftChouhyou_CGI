#!/bin/bash -xv
#
# COMMON_USERNAME_KENSAKU.CGI >>> ユーザーCDによりユーザー名検索
# Usage : COMMON_USERNAME_KENSAKU.CGI
#
# Written by Li.qingting(TRE・CHINA)  /Date : 25 July. 2016

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
cshld=${dir}/AP/SOFT_CHOUHYOU/CGI/COMMON_SHELL

# エラー時の終了処理定義
ERROR_EXIT(){
  echo '{"error":"1"}'
  exit 1
}

echo "Content-Type:text;charset=UTF-8"
echo ""

dd count=$CONTENT_LENGTH bs=1 | 
qsstr -l_ -i_                 > $tmp-param
[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT

# パラメータ定義
usercd=$(readvalue -uUSERCD $tmp-param | fmtfixed -c1 -w10)
[ -z ${usercd} ] && ERROR_EXIT

shl=COMMON_USERNAME_KENSAKU.SEARCH
${shld}/${shl} ${usercd} > $tmp-username
# 1.ユーザー名
[ $? -eq 0 ] || ERROR_EXIT

#データを画面に表示
# 1.データファイル/ 2.対象名 3.データ種類(S:変数,F:ファイル)

error=0
cat << FIN > $tmp-datafile
${error} error S
$tmp-username username F
FIN

shl=COMMON_JSONDATA_OUT.SHELL
${cshld}/${shl} $tmp-datafile > $tmp-result
[ $? -eq 0 ] || ERROR_EXIT

cat $tmp-result                   
# 1.ユーザー名
[ $? -eq 0 ] || ERROR_EXIT

#/////////////////////////////////////////////////////////////////////////
# 終了部分
#/////////////////////////////////////////////////////////////////////////
# 終了
rm -rf $tmp-*

exit 0
