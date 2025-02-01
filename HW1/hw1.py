## Q1
# num = int(input("Enter a number: "))
# divisors = []
# for i in range(1, num + 1):
#     if num % i == 0:
#         divisors.append(i)
# print("Divisors:" , divisors)

## Q2
# count = 0
# total = 0
#
# while True:
#     num = int(input(f"Please enter number #{count + 1} " + (f"(avg={total // count}, Sum={total}): " if count > 0 else ": ")))
#
#     if num < 0:
#         break
#
#     count += 1
#     total += num
#
# print("Thank you. Goodbye.")

##Q3
# word_count = {}
#
# while True:
#     word = input(f'Please type a word: ')
#     word_lower = word.lower()
#     if word_lower in word_count:
#         word_count[word_lower] += 1
#     else:
#         word_count[word_lower] = 1
#     if word_count[word_lower] == 2:
#         print(f"You entered the word {word} twice!")
#     if word_count[word_lower] == 3:
#         print(f"You entered the word {word} 3 times! GoodBye! ")
#         break


##Q4
count1=0
count2=0

list1 = list(map(int,input("Enter numbers fot List 1 and seperate then with spaces: ").split()))
list2 = list(map(int,input("Enter numbers fot List 2 and seperate then with spaces: ").split()))

# for the challenge we need to check the minimum length and to follow that
min_len = min(len(list1),len(list2))

for i in range(min_len):
    if list1[i]>list2[i]:
        count1 +=1
    elif list2[i]>list1[i]:
        count2 +=1

if count1 > count2:
    print("List 1 have more larger numbers")
elif count2 > count1:
    print("List 2 have more larger numbers")
else:
    print("Both lists have the same number of larger numbers")

