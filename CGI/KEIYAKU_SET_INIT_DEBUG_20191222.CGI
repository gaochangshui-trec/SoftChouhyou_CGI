#!/bin/bash -xv
#
# KEIYAKU_SET_INIT.CGI >>> JAN階層情報抽出
# Usage : KEIYAKU_SET_INIT.CGI
#
# Written by Li.Dan(TRE・CHINA)  /Date : 19 Jan. 2019

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
dir=/home/trial
shld=${dir}/AP/SOFT_CHOUHYOU/CGI
cshld=${dir}/AP/SOFT_CHOUHYOU/CGI/COMMON_SHELL

tmp=/tmp/$$-$(basename $0)_$(date +%Y%m%d)_$(date +%H%M%S)

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

userid=$(readvalue -uUSERCD $tmp-param)
[ -z ${userid} ] && ERROR_EXIT
[ ${userid} == "_" ] && ERROR_EXIT

kisetuflg=$(readvalue -uKISETUFLG $tmp-param)
[ -z ${kisetuflg} ] && kisetuflg=false

if [ ${kisetuflg} == false ];then
  #テーマ階層情報検索
  shl=KEIYAKU_SET_INIT_KAISO_KENSAKU.SEARCH
  ${shld}/${shl} $tmp > $tmp-jankaiso
  # 1.親ノードID 2.子ノードID 3.子ノード名 4.checkflg 5.階層FLG 6.openflg 7.親ノードFLG
  [ $? -eq 0 ] || ERROR_EXIT
  
  shl=KEIYAKU_SET_INIT_KAISO_JSON_MAKE.SEARCH
  ${shld}/${shl} $tmp-jankaiso false > $tmp-kaiso_tree
  [ $? -eq 0 ] || ERROR_EXIT

  treedata=$(cat $tmp-kaiso_tree)
else
  treedata=[]
fi

error=0
cat << FIN > $tmp-datafile
${error} error S 0
${treedata} treedata S 1
FIN

shl=COMMON_TOJSON.SHELL
${cshld}/${shl} $tmp-datafile > $tmp-result
[ $? -eq 0 ] || ERROR_EXIT

cat $tmp-result

#/////////////////////////////////////////////////////////////////////////
# 終了部分
#/////////////////////////////////////////////////////////////////////////
# 終了
rm -rf $tmp-*

exit 0
