nb_vars = 10
nb_contr = 10
nb_vals = 15
nb_tuples = 30
nb_res = 3

# naming the files by tuple, name them by multiple
# variables if using several for loops
for tuple in 200 155 110 65 20
do
    ./urbcsp $nb_vars $nb_vals $nb_contr $tuple $nb_res > csp$tuple.txt
done
