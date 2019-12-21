#!/bin/bash -xv
#
# CHOUHYOU_SYUSEI_REG.CGI >>> キラー計画数情報登録
# Usage : CHOUHYOU_SYUSEI_REG.CGI
#
# Written by Li.dan(TRE・CHINA)  /Date : 9 Jan. 2019

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
lv4d=${dir}/APDATA/SOFT_CHOUHYOU/POMPA
killerd=${lv4d}/KILLER
masterd=${killerd}/MASTER
tbld=/SKCWEB/TBL
shld=${dir}/AP/SOFT_CHOUHYOU/CGI
cshld=${dir}/AP/SOFT_CHOUHYOU/CGI/COMMON_SHELL
tmp=/tmp/$$-$(basename $0)_$(date +%Y%m%d)_$(date +%H%M%S)
lockd=${dir}/APDATA/SOFT_CHOUHYOU/LOCK

apshld=/home/trial/AP/SHELL/SOFT_CHOUHYOU
stime=$(date +%Y%m%d%H%M%S)

hostip=$(readvalue -uTENSOU_DATA ${lv4d}/TBL/IP_CONFIG)
# エラー時の終了処理定義
ERROR_EXIT(){
  echo '{"error":"1"}'
  unlock -f ${lockd}/LOCK.CHOUHYOU_PLANQTY_REG.CGI
  ssh trial@${hostip} rm -rf ${apshld}/SET_SEMAPHORE/LOCK/CHOUHYOU_PLANQTY_REG.CGI </dev/null
  exit 1
}

echo "Content-Type:text;charset=UTF-8"
echo ""

dd count=$CONTENT_LENGTH bs=1 | 
qsstr -l_ -i_                 > $tmp-param
[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT

usercd=$(readvalue -uUSERID $tmp-param|fmtfixed -w10 -c1)
[ -z ${usercd} ] && ERROR_EXIT

flg=$(readvalue -uFLG $tmp-param) # DELETE/UPDATE
[ -z ${flg} ] && ERROR_EXIT

kikanid=$(readvalue -uKIKAN $tmp-param)
[ -z ${kikanid} ] && ERROR_EXIT

statusflg=$(readvalue -uSTATUSFLG $tmp-param) # 1:エラーの場合確認、2:エラーの場合登録できる 3:削除の場合
[ -z ${statusflg} ] && ERROR_EXIT
# 操作履歴作成
if [ ${flg} == "DELETE" ];then
  shl=CHOUHYOU_OPTION_HISTORY_KENSAKU.SEARCH
  ${shld}/${shl} 0002 $(basename $0) ${usercd}
  [ $? -eq 0 ] || ERROR_EXIT
else
  shl=CHOUHYOU_OPTION_HISTORY_KENSAKU.SEARCH
  ${shld}/${shl} 0001 $(basename $0) ${usercd}
  [ $? -eq 0 ] || ERROR_EXIT
fi

mkdir -p ${lockd}
lock -f ${lockd}/LOCK.CHOUHYOU_PLANQTY_REG.CGI

# 設定データ同期チェック
while true ; do
  if [ -e ${lockd}/LOCK.POMPAMAKE.DAYSOFT.DOUKI_KILLER_CHOUHYOUU ];then
    sleep 1
    echo ${lockd}/LOCK.POMPAMAKE.DAYSOFT.DOUKI_KILLER_CHOUHYOU_$(date +%Y%m%d)_$(date +%H%M%S)
  else
    break;
    echo ${lockd}/LOCK.POMPAMAKE.DAYSOFT.DOUKI_KILLER_CHOUHYOU_END
  fi 
:; done

:> $tmp-CHOUHYOU_PLANQTY_REG.CGI

#フォルダー作成
ssh trial@${hostip} mkdir -p ${apshld}/SET_SEMAPHORE/LOCK/

#セマフォ作成
scp $tmp-CHOUHYOU_PLANQTY_REG.CGI trial@${hostip}:${apshld}/SET_SEMAPHORE/LOCK/CHOUHYOU_PLANQTY_REG.CGI </dev/null

# 1.LV1の情報作成
shl=CHOUHYOU_COMMON_L1.LOGIN
${shld}/${shl} ${stime} ${usercd} $tmp-param
[ $? -eq 0 ] || ERROR_EXIT


# 1:期間ID 2:期間名 3:年 4:季節タイプ 
hejoin -k1 <(echo ${kikanid}) ${masterd}/COMMON/MST_KIKAN >$tmp-kikan
# 1:期間ID 2:期間名 3:年 4:季節タイプ
[ $(errchk ${PIPESTATUS[@]}) -ne 0 ] && ERROR_EXIT

year=$(selcol -c3 $tmp-kikan)
mode=$(selcol -c2 $tmp-kikan|substr -c1.5.2) # AW/SS
kisetutype=$(selcol -c4 $tmp-kikan) # 2/1

error=0
:> $tmp-error_style
:> $tmp-text_color
if [ ${flg} == "DELETE" ];then
  shl=CHOUHYOU_SYUSEI_DELETE_L4.LOGIN
  ${shld}/${shl} ${usercd} $tmp-param ${year} ${mode}
  [ $? -eq 0 ] || ERROR_EXIT

  #無駄なマスタ削除
  shl=CHOUHYOU_SYUSEI_DELETE_MST_MINTE_L4.LOGIN
  ${shld}/${shl} ${usercd} ${year} ${mode}
  [ $? -eq 0 ] || ERROR_EXIT
else
  cat $tmp-param                          |
  grep DATALIST                           |
  sed 's/%/ /g'                           |
  selcol -c1,2 -cNF                       |
  # 1.key1 2.key2 3.value
  toh -k1,2                               |
  # 1.key1 2.key2 3...value
  delcol -c1,2                            >$tmp-data_one
  # 1..NF.value
  [ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT

  col=$(colc $tmp-data_one)
  [ $? -eq 0 ] || ERROR_EXIT

  kuniq -k1,${col} $tmp-data_one  >$tmp-data
  [ $? -eq 0 ] || ERROR_EXIT
  :> $tmp-errorflg
  shl=CHOUHYOU_SYUSEI_REG.CHECK
  ${shld}/${shl} $tmp-data_one $tmp-text_color ${year} ${kisetutype} $tmp-errorflg > $tmp-error_style
  [ $? -eq 0 ] || ERROR_EXIT

  if [ ! -s $tmp-error_style -o ${statusflg} == "2" ] ;then
    # 1.LV4の情報作成
    shl=CHOUHYOU_SYUSEI_REG_L4.LOGIN
    ${shld}/${shl} ${usercd} $tmp-param $tmp-data ${mode} ${year}
    [ $? -eq 0 ] || ERROR_EXIT
    
    #年
    year=$(awk '$1=="'${kikanid}'"' ${lv4d}/KILLER/MASTER/COMMON/MST_KIKAN|selcol -c3)
    #季節タイプ(AW/SS)
    kisetutype=$(awk '$1=="'${kikanid}'"{print $4=="1"?"SS":"AW"}' ${lv4d}/KILLER/MASTER/COMMON/MST_KIKAN)
    #フォルダー作成
    ssh trial@${hostip} mkdir -p ${apshld}/SET_SEMAPHORE/LOGIN_STATUS_KILLER/
    #セマフォ作成
    :> $tmp-tensoflg

    div=$(readvalue -uDIVCD $tmp-param|fmtfixed -c1 -w4)
    line=$(readvalue -uLINECD $tmp-param|fmtfixed -w4 -c1)
    bumon=$(readvalue -uBUMONCD $tmp-param|fmtfixed -w4 -c1)
    categorycd=$(readvalue -uCATEGORYCD $tmp-param|fmtfixed -c1 -w4)
    tensod=${apshld}/SET_SEMAPHORE/LOGIN_STATUS_KILLER
    kaisod=${kisetutype}@${year}@${div}@${line}@${bumon}@${categorycd}
    scp $tmp-tensoflg trial@${hostip}:${tensod}/${kaisod}@@${usercd}_${stime} </dev/null
  else
    error=$(cat $tmp-errorflg)
    #error=2
  fi
fi

cat << FIN > $tmp-datafile
${error} error S _
$tmp-error_style color F _
$tmp-text_color text_color F _
FIN

shl=COMMON_TOJSON_WITHHEAD.SHELL
${cshld}/${shl} $tmp-datafile > $tmp-result
[ $? -eq 0 ] || ERROR_EXIT

cat $tmp-result

ssh trial@${hostip} rm -rf ${apshld}/SET_SEMAPHORE/LOCK/CHOUHYOU_PLANQTY_REG.CGI </dev/null

#/////////////////////////////////////////////////////////////////////////
# 終了部分
#/////////////////////////////////////////////////////////////////////////
# 終了

rm -rf $tmp-*
#ロックファイル削除
unlock -f ${lockd}/LOCK.CHOUHYOU_PLANQTY_REG.CGI

exit 0
