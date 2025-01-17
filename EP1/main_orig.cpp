/*
Trabalho Prático 1 - Fundamentos de Sistemas Paralelos e Distribuídos
Autor(a): Luiza de Melo Gomes
Matrícula: 2021040075
*/

#include <bits/stdc++.h>
#include <stdio.h>
#include <pthread.h>
#include <time.h>

using namespace std;

#define NUM_THREADS 1000
#define NUM_THREADS_AT_ROOM 3
#define NUM_ROOMS 11

/*
struct thread_data
- criada para armazenar dados de uma thread, como tempo de inicialização e número de salas a serem visitadas
- Dentro dessa estrutura um vetor de pares representa a ordem das salas a serem visitadas,
  sendo o primeiro número o identificador da sala, e o segundo o tempo em que a thread permanecerá na sala.
*/
typedef struct thread_data
{
    int id;
    int initial_time;
    int num_rooms;
    vector<pair<int, int>> rooms_order;
} thread_data;

int num_threads_waiting_to_enter[NUM_ROOMS];
int num_threads_in_room[NUM_ROOMS];
int num_threads_waiting_to_exit[NUM_ROOMS];

pthread_mutex_t room_mutex[NUM_ROOMS];
/*
room_condition
 - condição para controlar a entrada de uma thread somente quando houver 3 threads esperando para entrar na sala
room_empty
 - condição para controlar a entrada de uma thread somente quando a sala estiver vazia
*/
pthread_cond_t room_condition[NUM_ROOMS];
pthread_cond_t room_empty[NUM_ROOMS];
thread_data thread_data_array[NUM_THREADS];
pthread_t threads[NUM_THREADS];

void passa_tempo(int tid, int sala, int decimos)
{
    struct timespec zzz, agora;
    static struct timespec inicio = {0, 0};
    int tstamp;

    if ((inicio.tv_sec == 0) && (inicio.tv_nsec == 0))
    {
        clock_gettime(CLOCK_REALTIME, &inicio);
    }

    zzz.tv_sec = decimos / 10;
    zzz.tv_nsec = (decimos % 10) * 100L * 1000000L;

    if (sala == 0)
    {
        nanosleep(&zzz, NULL);
        return;
    }

    clock_gettime(CLOCK_REALTIME, &agora);
    tstamp = (10 * agora.tv_sec + agora.tv_nsec / 100000000L) - (10 * inicio.tv_sec + inicio.tv_nsec / 100000000L);

    printf("%3d [ %2d @%2d z%4d\n", tstamp, tid, sala, decimos);

    nanosleep(&zzz, NULL);

    clock_gettime(CLOCK_REALTIME, &agora);
    tstamp = (10 * agora.tv_sec + agora.tv_nsec / 100000000L) - (10 * inicio.tv_sec + inicio.tv_nsec / 100000000L);

    printf("%3d ) %2d @%2d\n", tstamp, tid, sala);
}

void *begin_thread_execution(void *arg)
{
    thread_data *t = (thread_data *)arg;

    // executando tempo de inicialização da thread
    passa_tempo(t->id, 0, t->initial_time);

    for (int room = 1; room <= t->num_rooms; room++)
    {
        int current_room = t->rooms_order[room - 1].first;
        int previous_room;

        if (room > 1)
        {
            previous_room = t->rooms_order[room - 2].first;
        }

        pthread_mutex_lock(&room_mutex[current_room]);

        // esperando a sala ficar vazia

        while (num_threads_in_room[current_room] > 0)
        {
            // printf("%d esperando sala vazia\n", t->id);
            pthread_cond_wait(&room_empty[current_room], &room_mutex[current_room]);
        }

        // esperando 3 threads pra entrar na sala
        num_threads_waiting_to_enter[current_room] += 1;
        if (num_threads_waiting_to_enter[current_room] < NUM_THREADS_AT_ROOM)
        {
            // printf("%d esperando thread pra entrar com %d threads na sala\n", t->id, num_threads_waiting_to_enter[current_room]);

            while (num_threads_waiting_to_enter[current_room] < NUM_THREADS_AT_ROOM)
            {
                pthread_cond_wait(&room_condition[current_room], &room_mutex[current_room]);
            }
        }
        else if (num_threads_waiting_to_enter[current_room] == NUM_THREADS_AT_ROOM)
        {
            // printf("%d sinalizou\n", t->id);
            for (int i = 0; i < NUM_THREADS_AT_ROOM - 1; i++)
            {
                pthread_cond_signal(&room_condition[current_room]);
            }
        }

        // libera a sala anterior, sinaliza para as threads que estão esperando e vai pra próxima sala
        if (room > 1)
        {
            num_threads_in_room[previous_room] -= 1;
            pthread_cond_signal(&room_empty[previous_room]);
        }

        num_threads_in_room[current_room] += 1;

        pthread_mutex_unlock(&room_mutex[current_room]);

        passa_tempo(t->id, t->rooms_order[room - 1].first, t->rooms_order[room - 1].second);

        pthread_mutex_lock(&room_mutex[current_room]);
        num_threads_waiting_to_enter[current_room] -= 1;

        // libera a sala atual, caso seja a última sala que a thread irá visitar
        if (room == t->num_rooms)
        {
            num_threads_in_room[current_room] -= 1;
            pthread_cond_signal(&room_empty[current_room]);
        }

        pthread_mutex_unlock(&room_mutex[current_room]);
    }

    return nullptr;
}

int main()
{

    for (int i = 0; i < NUM_ROOMS; i++)
    {
        pthread_mutex_init(&room_mutex[i], NULL);
        pthread_cond_init(&room_condition[i], NULL);
        pthread_cond_init(&room_empty[i], NULL);
    }

    int n_rooms, n_threads;

    cin >> n_rooms >> n_threads;

    for (int i = 0; i < n_threads; i++)
    {
        cin >> thread_data_array[i].id >> thread_data_array[i].initial_time >> thread_data_array[i].num_rooms;

        for (int j = 0; j < thread_data_array[i].num_rooms; j++)
        {
            pair<int, int> room;
            cin >> room.first >> room.second;

            thread_data_array[i].rooms_order.push_back(room);
        }
    }

    for (int i = 0; i < n_threads; i++)
    {
        // cout << "criando thread " << thread_data_array[i].id << endl;
        pthread_create(&threads[i], NULL, begin_thread_execution, (void *)&thread_data_array[i]);
    }

    for (int i = 0; i < NUM_ROOMS; i++)
    {
        pthread_cond_destroy(&room_condition[i]);
        pthread_cond_destroy(&room_empty[i]);
        pthread_mutex_destroy(&room_mutex[i]);
    }
    pthread_exit(NULL);

    return 0;
}