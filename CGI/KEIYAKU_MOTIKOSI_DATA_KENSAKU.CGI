#!/bin/bash -xv
#
# KEIYAKU_MOTIKOSI_DATA_KENSAKU.CGI >>> 持越し予定数メンテ画面データ検索
# Usage : KEIYAKU_MOTIKOSI_DATA_KENSAKU.CGI
#
# Written by Zhang.Yunfeng(TRE・CHINA) / Date : 28 Nov. 2019

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
tmp=/tmp/$$-$(basename $0)_$(date +%Y%m%d)_$(date +%H%M%S)
dir=/home/trial
kinodir=SOFT_CHOUHYOU
shld=${dir}/AP/${kinodir}/CGI
cshld=${dir}/AP/${kinodir}/CGI/COMMON_SHELL

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

# 操作履歴作成

# パラメータ定義
kikan=$(readvalue -uKIKAN $tmp-param)
[ -z ${kikan} ] && ERROR_EXIT

flg=$(readvalue -uFLG $tmp-param) # 1:検索、2：取込 3出力
[ -z ${flg} ] && ERROR_EXIT

if [ ${flg} -eq 2 ];then
  idflg=0002
else
  idflg=0001
fi

# 操作履歴作成
usercd=$(readvalue -uUSERID $tmp-param)
[ -z ${usercd} ] && ERROR_EXIT

shl=CHOUHYOU_OPTION_HISTORY_KENSAKU.SEARCH
${shld}/${shl} ${idflg} $(basename $0) ${usercd}
[ $? -eq 0 ] || ERROR_EXIT

if [ ${flg} -eq 2 ];then # 画面データ取り込み
  cat $tmp-param    |
  grep JANLIST      |
  sed 's/%/ /g'     |
  selcol -c1,2 -cNF |
  # 1.key1 2.key2 3.value
  toh -k1,2         |
  # 1.key1 2.key2 3...value
  delcol -c1,2      |
  # 1.JAN 2.持越し数
  sed 's/_/@/g'     |
  # 1.JAN 2.持越し数
  fmtfixed -w20 -c1 |
  kuniq -k1,2       > $tmp-jan_motikosi
  # 1.JAN 2.持越し数
  [ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT
  
  # 画面データ取り込み
  shl=KEIYAKU_MOTIKOSI_DATA_KENSAKU_TORIKOMI.SEARCH_DEBUG
  ${shld}/${shl} ${kikan} $tmp-jan_motikosi >$tmp-end_data
  [ $? -eq 0 ] || ERROR_EXIT
elif [ ${flg} -eq 3 ];then #持越し数出力
  :>$tmp-end_data
  # 出力データ抽出
  shl=KEIYAKU_MOTIKOSI_DATA_KENSAKU.SEARCH_DEBUG
  ${shld}/${shl} ${kikan}                   |
  delcol -c11                               |
  tail -n +2                                >$tmp-excel_data
  [ $? -eq 0 ] || ERROR_EXIT
  #持越し数出力
  shl=KEIYAKU_MOTIKOSI_EXCEL_FORMAT.SEARCH
  ${shld}/${shl} $tmp ${usercd} $tmp-excel_data ${kikan} > $tmp-urlfile
  [ $? -eq 0 ] || ERROR_EXIT
  url=$(cat $tmp-urlfile)
else
  # 画面データ抽出
  shl=KEIYAKU_MOTIKOSI_DATA_KENSAKU.SEARCH_DEBUG
  ${shld}/${shl} ${kikan} >$tmp-end_data
  [ $? -eq 0 ] || ERROR_EXIT
fi

error=0
if [ 1 == $(rowc $tmp-end_data) ];then
  echo '{"error":"2"}' 
  rm -rf $tmp-*
  exit 0
else
  echo "true" >/dev/null
fi

# 1.data 2.key 3.S:一つ値 F:ファイル 4.0:普通値 1:array _:無視
cat << FIN > $tmp-datafile
${error} error S 0
$tmp-end_data data F _
${url} excelurl S 0
FIN

shl=COMMON_TOJSON.SHELL
${cshld}/${shl} $tmp-datafile > $tmp-result
[ $? -eq 0 ] || ERROR_EXIT

cat $tmp-result  |
sed 's/@//g' > $tmp-showdata
[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT

cat $tmp-showdata
[ $? -eq 0 ] || ERROR_EXIT

#/////////////////////////////////////////////////////////////////////////
# 終了部分
#/////////////////////////////////////////////////////////////////////////
# 終了
rm -rf $tmp-* &>/dev/null
exit 0
