from sacred import Experiment
import subprocess

ex = Experiment('sacred_test')

@ex.automain
def main():
    subprocess.call("cd /home/lukas/work/MP2016MUE/graphdiff/ && echo $PWD && java -Xmx4G -jar target/graphdiff-1.0-SNAPSHOT.jar Brad_Pitt George_Clooney Leonardo_DiCaprio Scarlett_Johansson Johnny_Depp",shell=True)

#R_HOME=/usr/lib/R;LD_LIBRARY_PATH=/usr/lib/R/lib:/usr/lib/R/bin:/home/lukas/R/x86_64-pc-linux-gnu-library/3.2/rJava/jri:;R_SHARE_DIR=/usr/share/R/share;R_INCLUDE_DIR=/usr/share/R/include;R_DOC_DIR=/usr/share/R/doc
