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


def users_with_shared_movies(u, users):
    neighbours = {}

    flag = False
    number_of_shared_movies = 0

    for v_id, v in users.items():
        for rating_u in u:
            for rating_v in v:
                if rating_u.movie_id == rating_v.movie_id:
                    neighbours[v_id] = v
                    number_of_shared_movies += 1

                    if number_of_shared_movies == 200:
                        flag = True
                        break
            if flag:
                break

    return neighbours


def k_nearest_neighbours(u_id, u, users, k):
    neighbours = {}

    for v_id, v in users_with_shared_movies(u, users).items():
        if v_id != u_id:
            neighbours[v_id] = [v, (abs(pc_similarity(u_id, u, v_id, v)))]

    reversed(sorted(neighbours.items(), key=lambda x: x[1][1]))

    return {index: neighbours[index] for index in list(neighbours)[:k]}


def contain_movie(u, movie_id):
    for rating in u:
        if rating.movie_id == movie_id:
            return rating
    return None


def predict_movie_rating(u_id, users, movie_id):
    u = users[u_id]
    neighbours = k_nearest_neighbours(u_id, u, users, 35)

    mean_neighbours_rating = 0
    total_ratings = 0

    for neighbour in neighbours:
        rating = contain_movie(neighbour, movie_id)
        if rating is not None:
            mean_neighbours_rating += rating.rating_value
            total_ratings += 1

    if total_ratings != 0:
        mean_neighbours_rating = mean_neighbours_rating / total_ratings

    return mean_neighbours_rating


##########
#  Main  #
##########

if __name__ == '__main__':
    users, movies = init(1)

    print(str(predict_movie_rating('1', users, 6)))
