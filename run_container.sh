#! bin/bash
ssh-keygen -R [127.0.0.1]:35322;
ssh-keygen -R [127.0.0.1]:6789;
docker run -itd --name shlee_net \
    -p 35322:22 -p 6789:6789 \
    -v /Users/seonghwanlee/postech20s/networks/net_workdir:/net_workdir \
    uplsh580/net:debian10.3_gcc8.3.0_python3.7 /bin/bash;