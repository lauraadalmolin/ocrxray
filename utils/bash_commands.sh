for file in $(ls . | grep accsum_enginetessdata4);do                 echo "$file"cat $file | head -n6done > ~/landscape_blur_1px-tessdata4.txt  

for dir in */; do for png in $dir*.png; do  mv $png $(echo $png | cut -d. -f1).xml; done; done
