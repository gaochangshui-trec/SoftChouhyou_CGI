#!/bin/bash -xv
#
# KEIYAKU_FINAL_DATA_KENSAKU.CGI >>> 季節画面データ検索
# Usage : KEIYAKU_FINAL_DATA_KENSAKU.CGI
#
# Written by Tan.zhihui(TRE・CHINA) / Date : 23 Aug. 2019

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
lv4d=/home/trial/APDATA/SOFT_CHOUHYOU/POMPA
act_jand=${lv4d}/KISETU/MASTER/ACTIVE_JAN
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
usercd=$(readvalue -uUSERCD $tmp-param)
[ -z ${usercd} ] && ERROR_EXIT

shl=CHOUHYOU_OPTION_HISTORY_KENSAKU.SEARCH
${shld}/${shl} 0001 $(basename $0) ${usercd}
[ $? -eq 0 ] || ERROR_EXIT
# パラメータ定義
kikan=$(readvalue -uKIKAN $tmp-param)
[ -z ${kikan} ] && ERROR_EXIT

flg=$(readvalue -uFLG $tmp-param) # 1:階層設定、2：JAN入力、3：なし
[ -z ${flg} ] && ERROR_EXIT

cat $tmp-param            |
grep SYODANSYA            |
kuniq -k2                 |
# 商談者
hejoin -v -k1 <(echo "_") > $tmp-stodansya
[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT

cat $tmp-param            |
grep KISETUTYPE           |
kuniq -k2                 > $tmp-kisetutype
# 季節区分
[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT

if [ ${flg} -eq 1 ];then
   cat $tmp-param                                                   |
   grep KAISO_ID                                                    |
   selcol -c2 -c2 -c2 -c2 -c2                                       |
   substr -c1.5.4 -c2.9.4 -c3.13.4 -c4.17.4 -c5.21.4                |
   # 1.部門CD 1.ミニ部門CD 4.品種CD 5.品目CD 6.サブセグメントCD
   kuniq -k1,5                                                      |
   # 1.部門CD 2.ミニ部門CD 3.品種CD 4.品目CD 5.サブセグメントCD
   hejoin -k2,6 - ${tbld}/JAN_BUMON_MINIBUMON_HINSYU_HINMOKU_SUBSEG |
   # 1:Jan 2:部門CD 3:カテゴリCD 4:サブカテゴリCD 5:セグメントCD 6:サブセグメントCD
   kuniq -k1                                                        |
   # 1:Jan
   hejoin -k1 ${act_jand}/ACTIVE_JAN                                > $tmp-jan
   # 1:Jan
   [ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT
elif [ ${flg} -eq 2 ] ; then
   cat $tmp-param    |
   grep JANLIST      |
   selcol -c2        |
   # 1.JAN
   fmtfixed -w20 -c1 |
   kuniq -k1         > $tmp-jan
   [ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT
elif [ ${flg} -eq 3 ] ; then
   :> $tmp-jan
fi

:>$tmp-end_data

:> $tmp-textcolor
:> $tmp-datahead
:> $tmp-headname
:> $tmp-bgcolor
:> $tmp-groupheaders

shl=KEIYAKU_FINAL_DATA_KENSAKU.SEARCH
${shld}/${shl} ${kikan} $tmp-jan $tmp-kisetutype $tmp-stodansya $tmp-datahead $tmp-headname $tmp-groupheaders $tmp-bgcolor $tmp-centerhead $tmp-textcolor >$tmp-end_data 
[ $? -eq 0 ] || ERROR_EXIT

datacnt=$(rowc $tmp-end_data)

if [ ! -s $tmp-end_data ];then
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

# データ列名
datahead=$(cat $tmp-datahead |tov|toh -l'","'|awk '{print "[\""$1"\"]"}')
# 帳票ヘッダー
headname=$(cat $tmp-headname |tov|toh -l'","'|awk '{print "[\""$1"\"]"}')

centerhead=$(cat $tmp-centerhead)

error=0
# 1.data 2.key 3.S:一つ値 F:ファイル 4.0:普通値 1:array _:無視
cat << FIN > $tmp-datafile
${error} error S 0
${centerhead} merge_colNameStartNum S 1
$tmp-end_data info F _
${datahead} colname S _
${headname} headname S _
${datacnt} datacnt S 0
$tmp-groupheaders groupheaders F _
$tmp-bgcolor color F _
$tmp-textcolor textcolor F _
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
