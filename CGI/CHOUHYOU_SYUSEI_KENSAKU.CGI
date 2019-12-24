#!/bin/bash -xv
#
# CHOUHYOU_SYUSEI_KENSAKU.CGI >>> 修正データ抽出
# Usage : CHOUHYOU_SYUSEI_KENSAKU.CGI
#
# Written by Li.dan(TRE・CHINA) / Date : 10 Jan. 2019

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
lv4d=/home/trial/APDATA/SOFT_CHOUHYOU/POMPA
killerd=${lv4d}/KILLER
masterd=${killerd}/MASTER
tbld=/SKCWEB/TBL
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
kikanid=$(readvalue -uKIKAN $tmp-param)
[ -z ${kikanid} ] && ERROR_EXIT

div=$(readvalue -uDIVCD $tmp-param |fmtfixed -w4 -c1)
[ -z ${div} ] && ERROR_EXIT

line=$(readvalue -uLINE $tmp-param |fmtfixed -w4 -c1)
[ -z ${line} ] && ERROR_EXIT

bumon=$(readvalue -uBUMON $tmp-param |fmtfixed -w4 -c1)
[ -z ${bumon} ] && ERROR_EXIT

category=$(readvalue -uKATEGORI $tmp-param|fmtfixed -w4 -c1)
[ -z ${category} ] && ERROR_EXIT

# 1:期間ID 2:期間名 3:年 4:季節タイプ 
hejoin -k1 <(echo ${kikanid}) ${masterd}/COMMON/MST_KIKAN >$tmp-kikan
# 1:期間ID 2:期間名 3:年 4:季節タイプ
[ $(errchk ${PIPESTATUS[@]}) -ne 0 ] && ERROR_EXIT

year=$(selcol -c3 $tmp-kikan)
mode=$(selcol -c2 $tmp-kikan|substr -c1.5.2)

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
shl=CHOUHYOU_SYUSEI_KENSAKU.SEARCH
${shld}/${shl} ${mode} ${year} ${div} ${category} $tmp-data ${line} ${bumon}
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

cat $tmp-result    |
sed 's/@@@@@@@//g'
[ $? -eq 0 ] || ERROR_EXIT


#/////////////////////////////////////////////////////////////////////////
# 終了部分
#/////////////////////////////////////////////////////////////////////////
# 終了
rm -rf $tmp-*　&> /dev/null
exit 0
