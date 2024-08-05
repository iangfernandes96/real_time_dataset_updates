# Given a sorted list of integers and a target sum, find the single pair of integers within the list that add up to the target sum.
# There is only one valid pair of integers within the list that add up to the target sum.


input_list = [-3, -2, 0, 1, 2, 3, 5, 8]
target_sum = 10

# a + b = target_sum
# a, target_sum - a

a, b = None, None

# for i in range(len(input_list)):
#     for j in range(i+1, len(input_list)):
#         if input_list[i] + input_list[j] == target_sum:
#             a, b = input_list[i], input_list[j]
#             break

input_set = set(input_list)
for ele in input_set:
    other_ele = target_sum - ele
    if other_ele in input_set:
        a, b = ele, other_ele
        break

print(a, b)
