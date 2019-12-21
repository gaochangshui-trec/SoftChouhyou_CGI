#!/bin/bash -xv
#
# CHOUHYOU_CATEGORYTENPO_EXCEL_KENSAKU.CGI >>>カテゴリ店舗別 データ抽出
# Usage : CHOUHYOU_CATEGORYTENPO_EXCEL_KENSAKU.CGI
#
# Written by Tan.zhihui(TRE・CHINA) / Date : 10 Sep. 2019

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
tbld=/SKCWEB/TBL
act_jand=/home/trial/APDATA/SKCS/POMPA/MASTER
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

# パラメータ定義

#期間設定情報
kikan=$(readvalue -uKIKAN $tmp-param)
[ -z ${kikan} ] && ERROR_EXIT

#ユーザCD
usercd=$(readvalue -uUSERCD $tmp-param)
[ -z ${usercd} ] && ERROR_EXIT

#ディビジョン情報
divid=$(readvalue -uDIVID $tmp-param)
[ -z ${divid} ] && ERROR_EXIT

echo ${divid} > $tmp-divid
[ ${divid} == "_" ] && > $tmp-divid

# 操作履歴作成
shl=CHOUHYOU_OPTION_HISTORY_KENSAKU.SEARCH
${shld}/${shl} 0001 $(basename $0) ${usercd}
[ $? -eq 0 ] || ERROR_EXIT

:> $tmp-out_headname
:> $tmp-out_colname
:> $tmp-out_groupheaders
:> $tmp-out_info
:> $tmp-out_color
:> $tmp-out_mergecell
:> $tmp-detail_data #値下げカラー用

cat << FIN > $tmp-paramfile
in_1 $tmp-kisetutype KISETUTYPE
in_2 $tmp-divid _
in_3 $tmp-lineid LINEID
in_4 $tmp-bumonid BUMONID
in_5 $tmp-gategoryid CATEGORYID
in_6 $tmp-sitenid SITENID
in_7 $tmp-zoneid ZONEID
in_8 $tmp-areaid AREAID
in_9 $tmp-tenid TEN_ID
out_1 $tmp-out_headname _
out_2 $tmp-out_colname _
out_3 $tmp-out_groupheaders _
out_4 $tmp-out_info _
out_5 $tmp-out_color _
out_6 $tmp-detail_data _
FIN


echo "r1 c1 r2 c2 color" > $tmp-out_color

#パラメータファイル加工
shl=CHOUHYOU_KILLER_EXCEL_INPUT_KENSAKU.SEARCH
${shld}/${shl} $tmp-param $tmp-paramfile
[ $? -eq 0 ] || ERROR_EXIT

shl=CHOUHYOU_CATEGORYTENPO_EXCEL_KENSAKU.SEARCH
${shld}/${shl} ${kikan} $tmp-paramfile
[ $? -eq 0 ] || ERROR_EXIT

if [ ! -s $tmp-out_info ];then
  echo '{"error":"2"}'
  rm -rf $tmp-*
  exit 1
else
  echo "true" >/dev/null
fi

shl=CHOUHYOU_CATEGORYTENPO_EXCEL_DISCOUNT_COLOR_KENSAKU.SEARCH
${shld}/${shl} ${kikan} $tmp-paramfile
[ $? -eq 0 ] || ERROR_EXIT

shl=CHOUHYOU_CATEGORYTENPO_EXCEL_FORMAT.SEARCH
${shld}/${shl} $tmp ${usercd} $tmp-paramfile > $tmp-urlfile
[ $? -eq 0 ] || ERROR_EXIT

error=0

url=$(cat $tmp-urlfile)
# 1.data 2.key 3.S:一つ値 F:ファイル 4.0:普通値 1:array _:無視
cat << FIN > $tmp-datafile
${error} error S 0
${url} excelurl S 0
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
