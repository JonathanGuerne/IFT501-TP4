import math


###########
# CLASSES #
###########

class Rating:
    def __init__(self, user_id, movie_id, rating_value):
        self.movie_id = movie_id
        self.user_id = user_id
        self.rating_value = rating_value


###########
#  FUNC.  #
###########

def init(index_doc):
    users = {}
    movies = {}
    with open('./u' + str(index_doc) + '.base', 'r', encoding='utf-8') as fin:
        for line in fin:
            line_array = line.split("\t")

            if line_array[0] not in users.keys():  # Check if the user already exists
                users[line_array[0]] = []

            if line_array[1] not in movies.keys():
                movies[line_array[1]] = []

            rating = Rating(line_array[0], line_array[1], line_array[2])

            users[line_array[0]].append(rating)  # Add the rating to the document
            movies[line_array[1]].append(rating)

    return users, movies


def test_recommendation(index):
    users = {}

    with open('./u' + str(index) + '.test', 'r', encoding='utf-8') as fin:
        for line in fin:
            line_array = line.split("\t")

            if line_array[0] not in users.keys():  # Check if the user already exists
                users[line_array[0]] = []

            rating = Rating(line_array[0], line_array[1], line_array[2])

            users[line_array[0]].append(rating)  # Add the rating to the document

    return users


def mean_rating(u):
    mean = 0

    for rating in u:
        mean += int(rating.rating_value)

    mean = mean / len(u)

    return mean


def find_shared_movies(u, v):
    shared_movies = []

    for rating_u in u:
        for rating_v in v:
            if rating_u.movie_id == rating_v.movie_id:
                shared_movies.append(movies[rating_v.movie_id])

    return shared_movies


def find_rating_variance(u_id, mean_rating, movie):
    for rating in movie:
        if rating.user_id == u_id:
            return int(rating.rating_value) - mean_rating
    return IndexError


def pc_similarity(u_id, u, v_id, v):
    shared_movies = find_shared_movies(u, v)

    mid_u_rating = mean_rating(u)
    mid_v_rating = mean_rating(v)

    numerator = 0

    denominator_u = 0
    denominator_v = 0

    for movie in shared_movies:
        numerator += find_rating_variance(u_id, mid_u_rating, movie) * find_rating_variance(v_id, mid_v_rating, movie)

        denominator_u += math.pow(find_rating_variance(u_id, mid_u_rating, movie), 2)
        denominator_v += math.pow(find_rating_variance(v_id, mid_v_rating, movie), 2)

    denominator = math.sqrt(denominator_u * denominator_v)

    if numerator == 0:
        return 0
    return numerator / denominator


def users_with_shared_movies(u, users):
    neighbours = {}
    flag = False

    for v_id, v in users.items():
        number_of_shared_movies = 0

        for rating_u in u:
            for rating_v in v:
                if rating_u.movie_id == rating_v.movie_id:
                    neighbours[v_id] = v
                    number_of_shared_movies += 1

                    if number_of_shared_movies == 1:
                        flag = True
                        break
            if flag:
                break

    return neighbours


def k_nearest_neighbours(u_id, u, users, k, movie_id, possible_neighbours, user_similaity_list):
    neighbours = {}

    for v_id, v in possible_neighbours.items():
        if v_id != u_id:
            if contain_movie(v, movie_id) is not None:
                neighbours[v_id] = [v, user_similarity_list[v_id]]

    reversed(sorted(neighbours.items(), key=lambda x: x[1][1]))

    return {index: neighbours[index] for index in list(neighbours)[:k]}


def contain_movie(u, movie_id):
    for rating in u:
        if rating.movie_id == movie_id:
            return rating
    return None


def list_similairty_user(possible_neighbours, u_id, u):
    user_similarity_list = {}
    for v_id, v in possible_neighbours.items():
        user_similarity_list[v_id] = pc_similarity(u_id,u,v_id,v)
    return user_similarity_list

def predict_movie_rating(u_id, users, movie_id, possible_neighbours,user_similarity_list):
    u = users[u_id]

    mean_neighbours_rating = 0
    sum_weights = 0

    neighbours = k_nearest_neighbours(u_id, u, users, 20, movie_id, possible_neighbours,user_similarity_list)

    for neighbour_id, neighbour_all_data in neighbours.items():

        neighbour = neighbour_all_data[0]
        similarity_with_neighbour = neighbour_all_data[1]

        rating = contain_movie(neighbour, movie_id)
        if rating is not None:
            mean_neighbours_rating += int(rating.rating_value) * similarity_with_neighbour
            sum_weights += abs(similarity_with_neighbour)

    if sum_weights != 0:
        mean_neighbours_rating = mean_neighbours_rating / sum_weights

    return mean_neighbours_rating


##########
#  Main  #
##########

if __name__ == '__main__':

    for i in range(2, 6):
        users, movies = init(i)
        users_solution = test_recommendation(i)

        sum_error = 0
        nb_rating = 0
        percentage = 0

        for nb in range(2):

            for u_id, sol_u in users_solution.items():

                u = users[u_id]

                possible_neighbours = users_with_shared_movies(u, users)
                user_similarity_list = list_similairty_user(possible_neighbours, u_id, u)

                for rating in sol_u:
                    prediction = (predict_movie_rating(u_id, users, rating.movie_id, possible_neighbours,user_similarity_list))
                    sum_error += abs(prediction - int(rating.rating_value))
                    nb_rating += 1

                percentage += 1 / len(users_solution) * 100
                print(percentage)

            error = sum_error / nb_rating

            print("\n")

            print("error for doc/test " + str(i) + " : " + str(error))

            print("\n")

            percentage = 0
