def func4(rdx,rsi,rdi):
    rax=rdx-rsi
    rcx=rax>>31
    rax=(rax+rcx)>>1
    rcx=rax+rsi
    if rdi==rcx:
        return 0;
    if rdi<rcx:
        return func4(rcx-1,rsi,rdi)*2
    else:
        return func4(rdx,rcx+1,rdi)*2+1

if __name__=='__main__':
    for i in range (0,15):
        if func4(14,0,i)==0:
            print(i)
        

              
          
      