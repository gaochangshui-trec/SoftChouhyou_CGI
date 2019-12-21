#!/bin/bash -xv
#
# CHOUHYOU_SYUHIN_DATA_KENSAKU.CGI >>> データ初期化表示
# Usage : CHOUHYOU_SYUHIN_DATA_KENSAKU.CGI
#
# Written by Li.dan(TRE・CHINA) / Date : 20 Dec. 2018

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
usercd=$(readvalue -uUSERID $tmp-param)
[ -z ${usercd} ] && ERROR_EXIT

shl=CHOUHYOU_OPTION_HISTORY_KENSAKU.SEARCH
${shld}/${shl} 0001 $(basename $0) ${usercd}
[ $? -eq 0 ] || ERROR_EXIT
# パラメータ定義
kikan=$(readvalue -uKIKAN $tmp-param)
[ -z ${kikan} ] && ERROR_EXIT

kisetutype=$(readvalue -uKISETUTYPE $tmp-param)
echo ${kisetutype}                |
sed 's/,/ /g'                  |
tov                            |
kuniq -k1                      >$tmp-kisetu_list
[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT


:> $tmp-divfile
:> $tmp-linefile
:> $tmp-bumonfile
:> $tmp-categoryfile

#ディビジョン
divinfo=$(readvalue -uDIVLIST $tmp-param)
[ -z ${divinfo} ] && divinfo="_"
if [ ${divinfo} != "_" ];then
  #DIVリスト
  echo ${divinfo}                |
  sed 's/,/ /g'                  |
  tov                            |
  kuniq -k1                      >$tmp-divfile
  [ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT
else
  echo "true" >/dev/null
fi

#ライン
lineinfo=$(readvalue -uLINELIST $tmp-param)
[ -z ${lineinfo} ] && lineinfo="_"
if [ ${lineinfo} != "_" ];then
  #DIVリスト
  echo ${lineinfo}               |
  sed 's/,/ /g'                  |
  tov                            |
  kuniq -k1                      >$tmp-linefile
  [ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT
else
  echo "true" >/dev/null
fi

#部門
bumoninfo=$(readvalue -uBUMONLIST $tmp-param)
[ -z ${bumoninfo} ] && bumoninfo="_"
if [ ${bumoninfo} != "_" ];then
  #DIVリスト
  echo ${bumoninfo}              |
  sed 's/,/ /g'                  |
  tov                            |
  kuniq -k1                      >$tmp-bumonfile
  [ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT
else
  echo "true" >/dev/null
fi

#カテゴリ
categoryinfo=$(readvalue -uCATEGORYLIST $tmp-param)
[ -z ${categoryinfo} ] && categoryinfo="_"
if [ ${categoryinfo} != "_" ];then
  #DIVリスト
  echo ${categoryinfo}           |
  sed 's/,/ /g'                  |
  tov                            |
  kuniq -k1                      >$tmp-categoryfile
  [ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT
else
  echo "true" >/dev/null
fi

#登録者
loginuser=$(readvalue -uLOGINUSER $tmp-param|fmtfixed -c1 -w10)
[ ${loginuser} == "0000000000" ] && loginuser="_"

#開始週
beginweek=$(readvalue -uBEGINWEEK $tmp-param)
#終了週
endweek=$(readvalue -uENDWEEK $tmp-param)

#リストデータ加工
#echo ${datalist}   |
#sed 's/\],\[/ /g'  |
#sed 's/\]//g'      |
#sed 's/\[//g'      |
#tr ' ' '\n'        |
#sed 's/,/ /g'      > $tmp-list
#[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT

:> $tmp-data

# 商品情報抽出
shl=CHOUHYOU_SYOHIN_DATA_KENSAKU.SEARCH
${shld}/${shl} ${kikan} $tmp-kisetu_list $tmp-divfile $tmp-linefile $tmp-bumonfile $tmp-categoryfile ${loginuser} ${beginweek} ${endweek}   >$tmp-data
[ $? -eq 0 ] || ERROR_EXIT

error=0
#echo '[" "]' > $tmp-sted
#headname=$(toh -l'","' ${tmpf}/headname|crossjoin $tmp-sted - |awk '{print $1$3$2}')

# 1.data 2.key 3.S:一つ値 F:ファイル 4.0:普通値 1:array _:無視
cat << FIN > $tmp-datafile
${error} error S 0
$tmp-data data F _
FIN

shl=COMMON_TOJSON.SHELL
${cshld}/${shl} $tmp-datafile > $tmp-result
[ $? -eq 0 ] || ERROR_EXIT

cat $tmp-result
[ $? -eq 0 ] || ERROR_EXIT


#/////////////////////////////////////////////////////////////////////////
# 終了部分
#/////////////////////////////////////////////////////////////////////////
# 終了
rm -rf $tmp-*

exit 0
