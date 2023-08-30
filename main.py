import sqlite3

def connectionTest():
    # O connect() vai criar o arquivo db caso nao exista
    con = sqlite3.connect('botw.db')
    cursor = con.cursor()

    # Executando select e printanto resultados
    cursor.execute('SELECT * FROM people')
    rows = cursor.fetchall()
    for r in rows:
        print(r)

    # Verificar existencia da table
    # res = cursor.execute('SELECT name FROM sqlite_master')
    # res.fetchone() # puxa a primeira linha do resultado

    con.close()

    # a = 3

def menuPrint():
    '''
    Prints the program's main menu
    '''
    # Dictionary containing the menu options
    menuOptions = {
        1: 'list all episodes',
        2: 'search for an episode by title or number',
        3: 'list all featured movies and videos',
        4: 'search for a specific movie',
        5: 'search for a specific director',
        6: 'search for a host or combination of hosts'
    }
    print('\n+----------------------------+')
    print('| Best of the Worst database |')
    print('+----------------------------+\n')
    print('What are you looking for?')
    for key in menuOptions.keys():
        print(key, ' - ', menuOptions[key])
    print('Type the corresponding number: ')

def listAllEpisodes():
    '''
    Handles option 1 on the main menu, printing a simplified list of all episodes
    '''
    print('\nListing all episodes: ')
    con = sqlite3.connect('botw.db')
    cursor = con.cursor()
    cursor.execute('SELECT number, title, upload, length FROM episodes ORDER BY number')
    rows = cursor.fetchall()
    for r in rows:
        print('{:<3}'.format(str(r[0])), r[2], '{:>8}'.format(r[3]), r[1])
    con.close()

def printEpisodesDetailed(query,desc):
    '''
    This function prints a list of episodes with corresponding hosts and movies/videos, according to a user-made query
    :param query: string, the sql query, which is necessarily one that returns entries in the episodes table
    :param desc: integer, if 1 includes description field in results; if 2, does not include them
    '''
    con = sqlite3.connect('botw.db')
    cursor = con.cursor()
    cursor2 = con.cursor()

    cursor.execute(query)
    rows = cursor.fetchall()

    print(len(rows), ' results found.\n') # Prints number of rows

    # Basic episode info is printed on a loop whose iterations vary on whether description field is included
    if desc == 1:
        length = len(rows[0]) - 2
        end = -2
    else:
        length = len(rows[0]) - 1
        end = -1
    for r in rows:
        for i in range(length):
            print(r[i], end=' - ')
        print(r[end])

        # Executes a query for the hosts of the episode
        hostsList = 'Hosted by: '
        cursor2.execute('select p.name from people p join hosts_episodes h JOIN episodes e on h.p_id = p.p_id and h.ep_number = e.number where e.number = ' + str(r[0]))
        hostsQuery = cursor2.fetchall()

        # Formats the list of hosts into a single string and then prints it
        for i in range(len(hostsQuery) - 1):
            hostsList = hostsList + str(hostsQuery[i][0]) + ', '
        hostsList = hostsList + str(hostsQuery[-1][0])
        print(hostsList)

        # Executes a query for the movies/videos featured
        moviesList = 'Movies/videos watched: \n'
        cursor2.execute('select m.title, m.year, m.director from movies m join episodes e on m.episode = e.number where e.number = ' + str(r[0]))
        moviesQuery = cursor2.fetchall()

        # Formatting and printing the list of films/videos from the episode
        print('Movies/videos watched:')
        for m in moviesQuery: # Some videos don't have year or director info, this is handled here
            line = m[0]
            if m[1] != None:
                line = line + ' (' + str(m[1]) + ') '
            if m[2] != None:
                line = line + 'Dir. ' + m[2]
            print(line)

        if desc == 1: # Episode description, if requested, is printed in a separate line at the end
            print('Description: \n' + r[-1] + '\n') 
    con.close()

def lookForEpisode():
    '''
    Handles option 2 in the main menu, when user wants to look up a specific episode
    '''
    ep = input('\nType episode number or title (doesn''t have to be the full title)\n')
    desc = 0
    while desc != 1 and desc != 2:
        desc = int(input('Press 1 to include description in results, 2 to not include it'))

    query = 'select e.number, e.title, e.upload, e.length'

    if ep.isdigit(): # If user inputs a number, fetches that specific episode
        if desc == 1:
            query = query + ', e.description from episodes e where e.number = ' + ep
        else:
            query = query + ' from episodes e where e.number = ' + ep
    else: # If user inputs a title, multiple results may return
        if desc == 1:
            query = query + ', e.description from episodes e where e.title like \'%' + ep + '%\''
        else:
            query = query + ' from episodes e where e.title like \'%' + ep + '%\''

    print('')
    printEpisodesDetailed(query,desc)

def printMovies(query,order):
    '''
    Function that prints out a movie or list of movies, according to a user-made query
    :param query: a sql query that returns entries in the movies table
    '''
    con = sqlite3.connect('botw.db')
    cursor = con.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    for r in rows:
        line = r[0] + ' '
        if r[1] != None:
            line = line +  ' (' + str(r[1]) + ') '
        if r[2] != None:
            line = line + 'Dir. ' + r[2] + ' '
        line = line + '(ep. ' + str(r[3]) +')'
        print(line)        
    con.close()

def listAllMovies():
    '''
    Handles option 3 in the main menu: listing all featured movies and videos
    Essentially it adjusts the query and then calls the function that performs and prints it
    '''
    orderOptions = {
        1: 'By episode',
        2: 'Alphabetical',
        3: 'Chronological',
        4: 'By director'
    }
    op = 0
    print('Listing all movies\nSelect ordering: ')
    for key in orderOptions:
        print(key, ' - ', orderOptions[key])
    while int(op) not in orderOptions.keys():
        op = input()
    if op == '1':
        printMovies('SELECT title, year, director, episode FROM movies ORDER BY episode',2)
    elif op == '2':
        printMovies('SELECT title, year, director, episode FROM movies ORDER BY title',1)
    elif op == '3': # Videos with unknown year of release should go last
        printMovies('SELECT title, year, director, episode FROM movies WHERE year is not null ORDER BY year',3)
        print('\nThe following ones have unknown release years:\n')
        printMovies('SELECT title, year, director, episode FROM movies WHERE year is null ORDER BY title',1)
    elif op == '4': # Videos with unknown director should go last
        printMovies('SELECT title, year, director, episode FROM movies WHERE director is not null ORDER BY director',4)
        print('\nThe following ones have unknown directors:\n')
        printMovies('SELECT title, year, director, episode FROM movies WHERE director is null ORDER BY title',1)

def main():
    while(True):
        menuPrint()
        op = ''
        try:
            op = int(input())
        except:
            print('Wrong input. Please select one of the options presented')
        if op == 1:
            listAllEpisodes()
        elif op == 2:
            lookForEpisode()
        elif op == 3:
            listAllMovies()

main()
