import functools

lst=["shubham","abcdefg","joshi"]

def check(a,b):
    if len(a)>len(b):
        return 1
    elif len(a)==len(b):
        return ord(a[0])-ord(b[0])
    else:
        return -1
        
        
print(sorted(lst,key=functools.cmp_to_key(check)))
