'''def size(x): # lambda used instead (locally defined function)
    if x > 4:
        return x
    else:
        None
'''
sequences = [10,2,8,7,5,4,3,11,0, 1]
filtered_result = filter (lambda x: x > 4, sequences) 
print(list(filtered_result))


def myfunc(n):
  return len(n)

x = map(myfunc, ('apple', 'banana', 'cherry'))
print(list(x))

x = map(lambda x : len(x),('apple', 'banana', 'cherry'))
print(list(x))
