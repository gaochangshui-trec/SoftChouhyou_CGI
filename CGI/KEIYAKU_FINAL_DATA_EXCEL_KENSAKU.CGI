#!/bin/bash -xv
#
# KEIYAKU_FINAL_DATA_EXCEL_KENSAKU.CGI >>> 契約帳票画面EXCEL出力
# Usage : KEIYAKU_FINAL_DATA_EXCEL_KENSAKU.CGI
#
# Written by Tan.zhihui(TRE・CHINA) / Date : 27 Aug. 2019
# Alter by Zhang.Yunfeng(TRE・CHINA) / Date : 2 Dec. 2019

#/////////////////////////////////////////////////////////////////////////
# 初期設定
#/////////////////////////////////////////////////////////////////////////

# 環境変数設定
export PATH=/home/SMART:/home/SMART_TRIAL:/usr/local/bin:${PATH}
export LANG=ja_JP.UTF-8

# ログディレクトリ設定
cgishld=/home/trial/AP/SOFT_CHOUHYOU
logd=${cgishld}/LOG

# 走行ログの記録
echo   "${logd}/LOG.$(basename $0).$(date +%Y%m%d)_$(date +%H%M%S)_$$" &>/dev/null
exec 2> ${logd}/LOG.$(basename $0).$(date +%Y%m%d)_$(date +%H%M%S)_$$

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

#/////////////////////////////////////////////////////////////////////////
# 処理部分
#/////////////////////////////////////////////////////////////////////////

echo "Content-Type:text;charset=UTF-8"
echo ""

#画面から入力のデータ取得
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

usercd=$(readvalue -uUSERCD $tmp-param|fmtfixed -w10 -c1)
[ -z ${usercd} ] && ERROR_EXIT

#消化率項目（持越し抜き）1：抜き
motikosiflg=$(readvalue -uMOTOKOSIFLG $tmp-param)
[ -z ${motikosiflg} ] && ERROR_EXIT

cat $tmp-param                                            |
grep SYODANSYA                                            |
kuniq -k2                                                 > $tmp-stodansya
# 商談者
[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT
cat $tmp-param                                            |
grep KISETUTYPE                                           |
kuniq -k2                                                 > $tmp-kisetutype
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
:> $tmp-datahead
:> $tmp-headname
:> $tmp-merge_text
:> $tmp-bgcolor
:> $tmp-textcolor
shl=KEIYAKU_FINAL_DATA_EXCEL_KENSAKU.SEARCH
${shld}/${shl} ${kikan} $tmp-jan $tmp-kisetutype $tmp-stodansya $tmp-datahead $tmp-headname $tmp-merge_text $tmp-bgcolor $tmp-textcolor ${motikosiflg}>$tmp-end_data
[ $? -eq 0 ] || ERROR_EXIT

if [ ! -s $tmp-end_data ];then
  echo '{"error":"2"}'
  exit 0
  rm -rf $tmp-*
else
  echo "true" >/dev/null
fi

shl=KEIYAKU_FINAL_DATA_EXCEL_FORMAT.SEARCH
${shld}/${shl} $tmp $tmp-end_data ${usercd} $tmp-headname $tmp-merge_text $tmp-bgcolor $tmp-textcolor ${kikan} $tmp-kisetutype> $tmp-urlfile
[ $? -eq 0 ] || ERROR_EXIT

#echo '[" "]' > $tmp-sted
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

# 終了部分
#/////////////////////////////////////////////////////////////////////////
# 終了
#/////////////////////////////////////////////////////////////////////////
rm -rf $tmp-* &>/dev/null
exit 0
