source_dir=$1
dest_dir=$2

cd $source_dir

for f in *.tar.gz
do
    name="${f%-*}"

    full_dest_dir=$dest_dir/$name
    mkdir -p $full_dest_dir

    cp -n $f $full_dest_dir
done
