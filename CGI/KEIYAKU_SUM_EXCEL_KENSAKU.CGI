#!/bin/bash -xv
#
# KEIYAKU_SUM_EXCEL_KENSAKU.CGI >>> 契約集計帳票画面EXCEL出力
# Usage : KEIYAKU_SUM_EXCEL_KENSAKU.CGI
#
# Written by Gao.Changshui(TRE・CHINA) / Date : 28 Aug. 2019
# Modify  by Tan.zhihui(TRE・CHINA) / Date : 30 Aug. 2019
# Modify  by Zhang.Yunfeng(TRE・CHINA) / Date : 3 Dec. 2019

#/////////////////////////////////////////////////////////////////////////
# 初期設定
#/////////////////////////////////////////////////////////////////////////

#   環境変数設定
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
act_jand=/home/trial/APDATA/SKCS/POMPA/MASTER
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
# パラメータ定義
kikan=$(readvalue -uKIKAN $tmp-param)
[ -z ${kikan} ] && ERROR_EXIT

weekcd=$(readvalue -uWEEKCD $tmp-param) # 週CD
[ -z ${weekcd} ] && ERROR_EXIT

usercd=$(readvalue -uUSERCD $tmp-param|fmtfixed -w10 -c1)
[ -z ${usercd} ] && ERROR_EXIT

#契約数合計 1：あり ２：なし ３：すべて
totalnumflg=$(readvalue -uTOTALNUM $tmp-param)
[ -z ${totalnumflg} ] && ERROR_EXIT

#消化率項目（持越し抜き）1：抜き
motikosiflg=$(readvalue -uMOTOKOSIFLG $tmp-param)
[ -z ${motikosiflg} ] && ERROR_EXIT

cat $tmp-param                                            |
grep KISETUTYPE                                           |
kuniq -k2                                                 > $tmp-kisetutype
# 季節区分
[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT

# 操作履歴作成
shl=CHOUHYOU_OPTION_HISTORY_KENSAKU.SEARCH
${shld}/${shl} 0001 $(basename $0) ${usercd}
[ $? -eq 0 ] || ERROR_EXIT
:> $tmp-venderdata
:> $tmp-hinsyudata
shl=KEIYAKU_SUM_EXCEL_KENSAKU.SEARCH
${shld}/${shl} ${kikan} ${weekcd} $tmp-venderdata $tmp-hinsyudata $tmp-kisetutype ${motikosiflg} ${totalnumflg}
[ $? -eq 0 ] || ERROR_EXIT

shl=KEIYAKU_SUM_EXCEL_FORMAT.SEARCH
${shld}/${shl} $tmp ${usercd} $tmp-venderdata $tmp-hinsyudata ${weekcd} ${kikan} $tmp-kisetutype ${motikosiflg} ${totalnumflg}> $tmp-urlfile
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
