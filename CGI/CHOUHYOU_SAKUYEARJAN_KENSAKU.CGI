#!/bin/bash -xv
#
# CHOUHYOU_TEMALIST_KENSAKU.CGI >>> データ初期化表示
# Usage : CHOUHYOU_TEMALIST_KENSAKU.CGI
#
# Written by Gao.Changshui(TRE・CHINA) / Date : 08 Jun. 2019

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

shld=/home/trial/AP/SKCS/CGI
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
userid=$(readvalue -uUSERCD $tmp-param|fmtfixed -w10 -c1)
[ -z ${userid} ] && ERROR_EXIT

cat $tmp-param    |
grep "JANLIST"    |
grep -v "_"       |
selcol -c2        |
fmtfixed -w20 -c1 |
kuniq -k1         > $tmp-janlist
[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT

cat $tmp-param                          |
grep DATALIST                           |
sed 's/%/ /g'                           |
selcol -c1,2 -cNF                       |
# 1.key1 2.key2 3.value
toh -k1,2                               |
# 1.key1 2.key2 3...value
delcol -c1,2                            > $tmp-data
# 1..NF.value
# 1.DIV 2.ライン名 3.部門名 4.カテゴリ名 5.アイテム名 6.年 7.JAN 8.販売開始週 9.販売終了週 10.計画数
[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT

hejoin -v -k1,4 <(echo "_ _ _ _") $tmp-data    |
awk '$6=="今年"'                               |
# 1.DIV 2.ライン名 3.部門名 4.カテゴリ名 5.アイテム名 6.年 7.JAN 8.販売開始週 9.販売終了週 10.計画数
kuniq -k1,5                                    |
awk '{print $1,$2,$3,$4,$5,"昨年"}'            |
# 1.DIV 2.ライン名 3.部門名 4.カテゴリ名 5.アイテム名 6.年
crossjoin - $tmp-janlist                       |
# 1.DIV 2.ライン名 3.部門名 4.カテゴリ名 5.アイテム名 6.年 7.JAN
crossjoin - <(echo "_ _ _")                    |
# 1.DIV 2.ライン名 3.部門名 4.カテゴリ名 5.アイテム名 6.年 7.JAN 8.販売開始週 9.販売終了週 10.計画数
fmtfloat -c7                                   |
cat - $tmp-data                                |
kuniq -k1,10                                   |
ssort -k1,4@6                                  |
cat <(echo "F1 F2 F3 F4 F5 F6 F7 F8 F9 F10") - > $tmp-data_one
[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT

error=0
# 1.data 2.key 3.S:一つ値 F:ファイル 4.0:普通値 1:array _:無視
cat << FIN > $tmp-datafile
${error} error S 0
$tmp-data_one data F _
FIN

shl=COMMON_TOJSON.SHELL
${cshld}/${shl} $tmp-datafile > $tmp-result
[ $? -eq 0 ] || ERROR_EXIT

cat $tmp-result |
sed 's/_//g'
[ $? -eq 0 ] || ERROR_EXIT

#/////////////////////////////////////////////////////////////////////////
# 終了部分
#/////////////////////////////////////////////////////////////////////////
# 終了
rm -rf $tmp-*

exit 0
