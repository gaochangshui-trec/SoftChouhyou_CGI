#!/bin/bash -xv
#
# CHOUHYOU_TENPOCATEGORY_KENSAKU.CGI >>>店舗別カテゴリ別データ抽出
# Usage : CHOUHYOU_TENPOCATEGORY_KENSAKU.CGI
#
# Written by Tan.zhihui(TRE・CHINA) / Date : 02 Sep. 2019

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

# 操作履歴作成
usercd=$(readvalue -uUSERCD $tmp-param)
[ -z ${usercd} ] && ERROR_EXIT

shl=CHOUHYOU_OPTION_HISTORY_KENSAKU.SEARCH
${shld}/${shl} 0001 $(basename $0) ${usercd}
[ $? -eq 0 ] || ERROR_EXIT

:> $tmp-out_headname
:> $tmp-out_colname
:> $tmp-out_groupheaders
:> $tmp-out_info
:> $tmp-out_color 
:> $tmp-out_mergecell
:> $tmp-week_detail #明細データカラー用

cat << FIN > $tmp-paramfile
1 $tmp-kisetutype KISETUTYPE
2 $tmp-divid DIVID
3 $tmp-lineid LINEID
4 $tmp-bumonid BUMONID 
5 $tmp-gategoryid CATEGORYID 
6 $tmp-sitenid SITENID
7 $tmp-zoneid ZONEID 
8 $tmp-areaid AREAID
9 $tmp-tenid TEN_ID
10 $tmp-out_headname _
11 $tmp-out_colname _
12 $tmp-out_groupheaders _
13 $tmp-out_info _
14 $tmp-out_color _
15 $tmp-out_mergecell _
16 $tmp-week_detail _
FIN

#パラメータファイル加工
shl=CHOUHYOU_KILLER_INPUT_KENSAKU.SEARCH
${shld}/${shl} $tmp-param $tmp-paramfile 9
[ $? -eq 0 ] || ERROR_EXIT

#検索データ作成
shl=CHOUHYOU_TENPOCATEGORY_KENSAKU.SEARCH
${shld}/${shl} ${kikan} $tmp-paramfile
[ $? -eq 0 ] || ERROR_EXIT

datacnt=$(rowc $tmp-out_info)

if [ ! -s $tmp-out_info ];then
  echo '{"error":"2"}'
  rm -rf $tmp-*
  exit 0
elif [ ${datacnt} -ge 3000 ];then
  echo '{"datacnt":"'${datacnt}'"}'
  rm -rf $tmp-*
  exit 0
else
  echo "true" >/dev/null
fi

#連続5週ピークデータカラー作成
shl=CHOUHYOU_TENPOCATEGORY_COLOR_KENSAKU.SEARCH
${shld}/${shl} $tmp-paramfile
[ $? -eq 0 ] || ERROR_EXIT

#売変データカラー作成
shl=CHOUHYOU_TENPOCATEGORY_DISCOUNT_COLOR_KENSAKU.SEARCH
${shld}/${shl} ${kikan} $tmp-paramfile
[ $? -eq 0 ] || ERROR_EXIT

error=0

colname=$(cat $tmp-out_colname |tov|toh -l'","'|awk '{print "[\""$1"\"]"}')
headname=$(cat $tmp-out_headname |tov|toh -l'","'|awk '{print "[\""$1"\"]"}')

echo r1 c1 r2 c2 color |
cat - $tmp-out_color   > $tmp-out_color_final
[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT

# 1.data 2.key 3.S:一つ値 F:ファイル 4.0:普通値 1:array _:無視
cat << FIN > $tmp-datafile
${error} error S 0
${datacnt} datacnt S 0
$tmp-out_info info F _
${colname} colname S _
${headname} headname S _
$tmp-out_groupheaders groupheaders F _
$tmp-out_color_final color F _
$tmp-out_mergecell mergecell F _
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
