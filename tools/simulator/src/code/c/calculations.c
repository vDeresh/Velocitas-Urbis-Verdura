// #include <stdio.h>
#include <math.h>


// void process_coordinates(float (*track)[2], int num_coords) {
//     for (int i = 0; i < num_coords; i++) {
//         printf("Coordinate %d: (%f, %f)\n", i + 1, track[i][0], track[i][1]);
//     }
// }


float distanceBetweenVectors(float vec1[2], float vec2[2])
{
    return sqrtf(powf(vec1[0] - vec2[0], 2) + powf(vec1[1] - vec2[1], 2));
}


float distanceBetweenPoints(float (*track)[2], int p1, int p2)
{
    float distance = 0;

    for (int i = p1; i < p2; i++)
        distance += distanceBetweenVectors(track[i], track[i + 1]);

    return distance;
}