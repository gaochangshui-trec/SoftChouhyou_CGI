#!/bin/bash -xv
#
# CHOUHYOU_ALLCATEGORY_KENSAKU.CGI >>> 全体進捗画面データ抽出
# Usage : CHOUHYOU_ALLCATEGORY_KENSAKU.CGI 
#
# Written by Tan.zhihui(TRE・CHINA) / Date : 11 Sep. 2019

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

:> $tmp-out_colname
:> $tmp-out_info
:> $tmp-out_mergecell

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
10 $tmp-loginuser LOGINUSER
11 $tmp-out_colname _
12 $tmp-out_info _
13 $tmp-out_mergecell _
FIN

#パラメータファイル加工
shl=CHOUHYOU_KILLER_INPUT_KENSAKU.SEARCH
${shld}/${shl} $tmp-param $tmp-paramfile 10
[ $? -eq 0 ] || ERROR_EXIT

:> $tmp-bgcolor
shl=CHOUHYOU_ALLCATEGORY_KENSAKU.SEARCH
${shld}/${shl} ${kikan} $tmp-paramfile $tmp-bgcolor
[ $? -eq 0 ] || ERROR_EXIT

if [ ! -s $tmp-out_info ];then
  echo '{"error":"2"}' 
  rm -rf $tmp-*
  exit 0
else
  echo "true" >/dev/null
fi

error=0

# 1.data 2.key 3.S:一つ値 F:ファイル 4.0:普通値 1:array _:無視
cat << FIN > $tmp-datafile
${error} error S 0
$tmp-bgcolor color F _
$tmp-out_info info F _
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
