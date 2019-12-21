#!/bin/bash -xv
#
# CHOUHYOU_INITLOAD_KENSAKU.CGI >>>  画面初期データロード
# Usage : CHOUHYOU_INITLOAD_KENSAKU.CGI
#
# Written by Li.dan(TRE・CHINA) / Date : 29 July. 2019
# Modify  by Zhang.Yunfeng(TRE・CHINA) / Date : 18 Dec. 2019

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
lv4d=${dir}/APDATA/SOFT_CHOUHYOU/POMPA
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

#リストデータ加工
#echo ${datalist}   |
#sed 's/\],\[/ /g'  |
#sed 's/\]//g'      |
#sed 's/\[//g'      |
#tr ' ' '\n'        |
#sed 's/,/ /g'      > $tmp-list
#[ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT
tenflg=$(readvalue -uTENFLG $tmp-param) # 1:店舗関連情報表示 0:店舗関連情報表示しない
[ -z ${tenflg} ] && tenflg=0

janflg=$(readvalue -uJANFLG $tmp-param) # 1:JAN階層情報表示 0:JAN階層情報表示しない
[ -z ${janflg} ] && janflg=0

weekflg=$(readvalue -uWEEKFLG $tmp-param) # 1:週情報表示 0:週情報表示しない
[ -z ${weekflg} ] && weekflg=0

year=$(readvalue -uYEAR $tmp-param) # 年
[ -z ${year} ] && year="_"

kisetutype=$(readvalue -uKISETUTYPE $tmp-param) # AW/SS
[ -z ${kisetutype} ] && kisetutype="_"

chouhyoutype=$(readvalue -uCHOUHYOU_TYPE $tmp-param) # 帳票区分
[ -z ${chouhyoutype} ] && chouhyoutype="_"

#登録者(キラー)
userflg=$(readvalue -uUSERFLG $tmp-param)

#商談者(季節)
syodanflg=$(readvalue -uSYODANFLG $tmp-param)
[ -z ${syodanflg} ] && syodanflg="0"

:> $tmp-siten
:> $tmp-block
:> $tmp-area
:> $tmp-ten
:> $tmp-block_siten
:> $tmp-area_block
:> $tmp-ten_area

if [ ${tenflg} -eq 1 ];then
  # 1.店舗情報取得
  shl=CHOUHYOU_INITLOAD_KENSAKU_TENKAISO.SEARCH
  ${shld}/${shl} $tmp-siten $tmp-block $tmp-area $tmp-ten $tmp-block_siten $tmp-area_block $tmp-ten_area
  [ $? -eq 0 ] || ERROR_EXIT
else
  echo "true" >/dev/null
fi

:> $tmp-div
:> $tmp-line
:> $tmp-bumon
:> $tmp-category

if [ ${janflg} -eq 1 ];then
  # 1.JAN階層情報取得
  shl=CHOUHYOU_INITLOAD_KENSAKU_JANKAISO.SEARCH
  ${shld}/${shl} ${kisetutype} $tmp-div $tmp-line $tmp-bumon $tmp-category ${year}
  [ $? -eq 0 ] || ERROR_EXIT
else
  echo "true" >/dev/null
fi

:> $tmp-kikan
:> $tmp-kisetutype

if [ ${chouhyoutype} == "_" ];then
  echo "true" >/dev/null
else
  # 1.期間と季節区分情報取得
  shl=CHOUHYOU_INITLOAD_KENSAKU_KIKAN_KISETU.SEARCH
  ${shld}/${shl} ${chouhyoutype} $tmp-kikan $tmp-kisetutype
  [ $? -eq 0 ] || ERROR_EXIT
fi

:> $tmp-start_list
:> $tmp-end_list

if [ ${weekflg} -eq 1 ];then
  # 1.週リスト情報取得
  shl=CHOUHYOU_INITLOAD_KENSAKU_WEEKLIST.SEARCH
  ${shld}/${shl} ${year} $tmp-start_list $tmp-end_list
  [ $? -eq 0 ] || ERROR_EXIT
else
  echo "true" >/dev/null
fi

:>$tmp-user_data

if [ ${userflg} -eq 1 ];then
  # 1.登録者情報取
  shl=CHOUHYOU_INITLOAD_KENSAKU_USERINFO.SEARCH
  ${shld}/${shl} ${kisetutype} ${year} >$tmp-user_data
  [ $? -eq 0 ] || ERROR_EXIT
else
  echo "true" >/dev/null
fi

:> $tmp-syodansya
if [ ${syodanflg} -eq 1 ];then
  # 1.商談者取得
  shl=CHOUHYOU_INITLOAD_KENSAKU_SYODAN_AUTHOR.SEARCH
  ${shld}/${shl} ${kisetutype} ${year} > $tmp-syodansya
  [ $? -eq 0 ] || ERROR_EXIT
else
  echo "true" >/dev/null
fi

#季節集計帳票出力の週リスト作成
if [ ${chouhyoutype} == "KISETU" -a ${kisetutype} != "_" ];then
  #該当期間の終了日付
  begday=$(awk '$2=="'${year}${kisetutype}'"{print $3}' ${lv4d}/KISETU/MASTER/COMMON/MST_KISETU_UREZAIKO_KIKAN)
  endday=$(awk '$2=="'${year}${kisetutype}'"{print $4}' ${lv4d}/KISETU/MASTER/COMMON/MST_KISETU_UREZAIKO_KIKAN)
  if [ -z ${endday} ];then
    if [ ${kisetutype} == "SS" ];then
      begday=$[${year}-1]"1201"
      endday=${year}"1130"
    else
      begday=${year}"0601"
      endday=$[${year}+1]"0531"
    fi
  fi
  #該当期間の週
  begweek=$(sdate -w ${begday}d)
  endweek=$(sdate -w ${endday}d)

  echo ${lv4d}/KISETU/DATA/${kisetutype}/*/*/CHOUHYO_SHOW             |
  tov                                                                 |
  awk '$1!="${lv4d}/KISETU/DATA/'${kisetutype}'/*/*/CHOUHYO_SHOW"'    |
  awk '{print substr($1,length($1)-18,6),substr($1,length($1)-18,4)}' |
  #1.週 2.年
  awk '$1>="'${begweek}'"&&$1<="'${endweek}'"'                        |
  #1.週 2.年
  selcol -c1                                                          |
  #1.週
  LANG=C sort -k1,1nr                                                 |
  cat <(echo "weekcd") -                                              > $tmp-yearweek
  [ $(errchk ${PIPESTATUS[@]}) -eq 0 ] || ERROR_EXIT
else
  :> $tmp-yearweek
fi

error=0
#echo '[" "]' > $tmp-sted
#headname=$(toh -l'","' ${tmpf}/headname|crossjoin $tmp-sted - |awk '{print $1$3$2}')

# 1.data 2.key 3.S:一つ値 F:ファイル 4.0:普通値 1:array _:無視
cat << FIN > $tmp-datafile
${error} error S 0
$tmp-siten siten F _
$tmp-block block F _
$tmp-area area F _
$tmp-ten ten F _
$tmp-block_siten block_siten F _
$tmp-area_block area_block F _
$tmp-ten_area ten_area F _
$tmp-div div F _
$tmp-line line F _
$tmp-bumon bumon F _
$tmp-category category F _
$tmp-kikan kikan F _
$tmp-kisetutype kisetutype F _
$tmp-start_list startweek F _
$tmp-end_list endweek F _
$tmp-user_data user F _
$tmp-syodansya syodansya F _
$tmp-yearweek yearweek F _
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
