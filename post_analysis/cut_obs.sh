#!/bin/bash

loop_cut(){
  if [ ! -d $2 ];then
    echo $2
    mkdir -p $2
  fi
  for file in `ls $1`
  do
    srcfile=$1/$file
    dstfile=$2/$file
    if [ -e $srcfile ];then
      cut -d , -f -17 $srcfile>$dstfile
      #echo $srcfile
      echo $dstfile
    fi
  done
}

src="/public/home/buzh/PmQc/post_analysis/201903/obs_data"
dst="/public/home/buzh/PmQc/post_analysis/201903/obs_data_cut"

loop_cut $src $dst
