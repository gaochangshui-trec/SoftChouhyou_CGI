#!/bin/bash -xv
#
# KEIYAKU_JAN_MOTIKOSI_REG.CGI >>> 持越し数メンテ情報登録
# Usage : KEIYAKU_JAN_MOTIKOSI_REG.CGI
#
# Written by Zhang.Yunfeng(TRE・CHINA)  /Date : 2 Dec. 2019

#/////////////////////////////////////////////////////////////////////////
# 初期設定
#/////////////////////////////////////////////////////////////////////////


# 環境変数設定
export PATH=/home/SMART:/home/SMART_TRIAL:/usr/local/bin:${PATH}
export LANG=ja_JP.UTF-8

## ログディレクトリの定義
cgishld=/home/trial/AP/SOFT_CHOUHYOU
logd=${cgishld}/LOG

##走行ログの記録
echo "${logd}/LOG.$(basename $0).$(date +%Y%m%d)_$(date +%H%M%S)_$$" &>/dev/null
exec 2>${logd}/LOG.$(basename $0).$(date +%Y%m%d)_$(date +%H%M%S)_$$

# ディレクトリ定義
dir=/home/trial
shld=${dir}/AP/SOFT_CHOUHYOU/CGI
cshld=${dir}/AP/SOFT_CHOUHYOU/CGI/COMMON_SHELL
tmp=/tmp/$$-$(basename $0)_$(date +%Y%m%d)_$(date +%H%M%S)
lockd=${dir}/APDATA/SOFT_CHOUHYOU/LOCK
apshld=/home/trial/AP/SHELL/SOFT_CHOUHYOU

lv4d=/home/trial/APDATA/SOFT_CHOUHYOU/POMPA
hostip=$(readvalue -uTENSOU_DATA ${lv4d}/TBL/IP_CONFIG)
stime=$(date +%Y%m%d%H%M%S)

# エラー時の終了処理定義
ERROR_EXIT(){
  echo '{"error":"1"}'
  unlock -f ${lockd}/LOCK.KEIYAKU_JAN_MOTIKOSI_REG.CGI

  ssh trial@${hostip} rm -rf ${apshld}/SET_SEMAPHORE/LOCK/KEIYAKU_JAN_PLANQTY_REG.CGI </dev/null

  exit 1
}

echo "Content-Type:text;charset=UTF-8"
echo ""

dd count=$CONTENT_LENGTH bs=1 | 
qsstr -l_ -i_                 > $tmp-param
[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT

usercd=$(readvalue -uUSERID $tmp-param|fmtfixed -w10 -c1)
[ -z ${usercd} ] && ERROR_EXIT
# 操作履歴作成
shl=CHOUHYOU_OPTION_HISTORY_KENSAKU.SEARCH
${shld}/${shl} 0001 $(basename $0) ${usercd}
[ $? -eq 0 ] || ERROR_EXIT

kikan=$(readvalue -uKIKAN $tmp-param)
[ -z ${kikan} ] && ERROR_EXIT

#登録の期間チェック
shl=KEIYAKU_KIKAN_CHECK.SEARCH
${shld}/${shl} ${kikan} $tmp-rightkikan > $tmp-kikanchk
[ $? -eq 0 ] || ERROR_EXIT

if [ 0 == $(rowc $tmp-kikanchk) ];then
  rightkikan=$(toh -l, $tmp-rightkikan)
  echo '{"error":"2","rightkikan":"'${rightkikan}'"}' 
  rm -rf $tmp-*
  exit 0
else
  echo "true" >/dev/null
fi

mkdir -p ${lockd}
[ $? -eq 0 ] || ERROR_EXIT

lock -f ${lockd}/LOCK.KEIYAKU_JAN_MOTIKOSI_REG.CGI

# 設定データ同期チェック
while true ; do
  if [ -e ${lockd}/LOCK.POMPAMAKE.DAYSOFT.DOUKI_KISETU_CHOUHYOU ];then
    sleep 1
  else
    break;
  fi 
:; done

:> $tmp-KEIYAKU_JAN_PLANQTY_REG.CGI

#フォルダー作成
ssh trial@${hostip} mkdir -p ${apshld}/SET_SEMAPHORE/LOCK/

#セマフォ作成
scp $tmp-KEIYAKU_JAN_PLANQTY_REG.CGI trial@${hostip}:${apshld}/SET_SEMAPHORE/LOCK/KEIYAKU_JAN_PLANQTY_REG.CGI </dev/null

# 1.LV1の情報作成
shl=CHOUHYOU_COMMON_L1.LOGIN
${shld}/${shl} ${stime} ${usercd} $tmp-param
[ $? -eq 0 ] || ERROR_EXIT

cat $tmp-param                          |
grep DATALIST                           |
sed 's/%/ /g'                           |
selcol -c1,2 -cNF                       |
# 1.key1 2.key2 3.value
toh -k1,2                               |
# 1.key1 2.key2 3.value
delcol -c1,2                            >$tmp-data_one
# 1..NF.value
[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT

col=$(colc $tmp-data_one)
[ $? -eq 0 ] || ERROR_EXIT

kuniq -k1,${col} $tmp-data_one  >$tmp-data
[ $? -eq 0 ] || ERROR_EXIT

shl=KEIYAKU_JAN_MOTIKOSI_REG_L4.LOGIN
${shld}/${shl} ${usercd} $tmp-data ${kikan} 
[ $? -eq 0 ] || ERROR_EXIT

#フォルダー作成
ssh trial@${hostip} mkdir -p ${apshld}/SET_SEMAPHORE/LOGIN_STATUS_KISETU/
#セマフォ作成
scp $tmp-KEIYAKU_JAN_PLANQTY_REG.CGI trial@${hostip}:${apshld}/SET_SEMAPHORE/LOGIN_STATUS_KISETU/KEIYAKU_JAN_PLANQTY_REG.CGI_${usercd}_${stime} </dev/null

error=0
cat << FIN > $tmp-datafile
${error} error S 0
FIN

shl=COMMON_TOJSON_WITHHEAD.SHELL
${cshld}/${shl} $tmp-datafile > $tmp-result
[ $? -eq 0 ] || ERROR_EXIT

ssh trial@${hostip} rm -rf ${apshld}/SET_SEMAPHORE/LOCK/KEIYAKU_JAN_PLANQTY_REG.CGI </dev/null

cat $tmp-result

#/////////////////////////////////////////////////////////////////////////
# 終了部分
#/////////////////////////////////////////////////////////////////////////
# 終了

#ロックファイル削除
unlock -f ${lockd}/LOCK.KEIYAKU_JAN_MOTIKOSI_REG.CGI

rm -rf $tmp-* &>/dev/null
exit 0
