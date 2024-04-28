#include <math.h>
#include <stdio.h>
#include <stdlib.h>
// #include <time.h>
#include <sys/time.h>


void init(float _slipstream_effectiveness);

double handleSpeed(int alreadyTurning, double currentSpeed, double distanceToTurn, double tyreWear, double tyreType, double driversBrakingSkill, double referenceTargetSpeed, double mass, double downforce, double drag, double distanceToCarAhead, double speedOfCarAhead, double downforceOfCarAhead, float wasOvertaken);
double braking(double distanceToTurn, double driversBrakingSkill, double tyreWear, double referenceTargetSpeed, double mass, double downforce);
double realTargetSpeed(double referenceTargetSpeed, double mass, double downforce);
double acceleration(double drag, double tyreWear, double tyreType, double mass, double downforce, double distanceToCarAhead, double speedOfCarAhead, double downforceOfCarAhead, double speed, float wasOvertaken);
double maxSpeed(double drag, double mass, double downforce);

double slipstreamMultiplier(double distanceToCarAhead, double speedOfCarAhead, double downforceOfCarAhead, /*double currentSpeed,*/ float wasOvertaken);

double handleTyreWear(double tyreWear, int tyreType, double speed, double targetSpeed);


const int FPS = 60;
struct timeval t1;


#define NULL ((void *)0)

#define max(a, b)            \
({                           \
    __typeof__ (a) _a = (a); \
    __typeof__ (b) _b = (b); \
    _a > _b ? _a : _b;       \
})

#define min(a, b)            \
({                           \
    __typeof__ (a) _a = (a); \
    __typeof__ (b) _b = (b); \
    _a < _b ? _a : _b;       \
})



float SLIPSTREAM_EFFECTIVENESS;

void init(float _slipstream_effectiveness)
{
    SLIPSTREAM_EFFECTIVENESS = 1 / _slipstream_effectiveness;

    gettimeofday(&t1, NULL);
    srand(t1.tv_usec * t1.tv_sec);
}

// TODO
double handleSpeed(int alreadyTurning, double currentSpeed, double distanceToTurn, double tyreWear, double tyreType, double driversBrakingSkill,
             double referenceTargetSpeed, double mass, double downforce, double drag,
             double distanceToCarAhead, double speedOfCarAhead, double downforceOfCarAhead, float wasOvertaken)
{
    gettimeofday(&t1, NULL);
    srand(t1.tv_usec * t1.tv_sec);

    currentSpeed *= 2 * FPS;
    speedOfCarAhead *= 2 * FPS;

    // printf("%f", slipstream(distanceToCarAhead, speedOfCarAhead));

    double tempMaxSpeed = maxSpeed(drag, mass, downforce);

    if (alreadyTurning) {
        return (min(tempMaxSpeed, (min(realTargetSpeed(referenceTargetSpeed, mass, downforce), currentSpeed + acceleration(drag, tyreWear, tyreType, mass, downforce, distanceToCarAhead, speedOfCarAhead, downforceOfCarAhead, currentSpeed, wasOvertaken)))) - (rand() % 1001 / 1000)) / 2 / FPS;
    }

    double s1 = min(tempMaxSpeed, braking(distanceToTurn, driversBrakingSkill, tyreWear, referenceTargetSpeed, mass, downforce));
    double s2 = min(tempMaxSpeed, currentSpeed + acceleration(drag, tyreWear, tyreType, mass, downforce, distanceToCarAhead, speedOfCarAhead, downforceOfCarAhead, currentSpeed, wasOvertaken));

    return (min(s1, s2) - (rand() % 1001 / 1000)) / 2 / FPS;
}


double braking(double distanceToTurn, double driversBrakingSkill, double tyreWear, double referenceTargetSpeed, double mass, double downforce)
{
    return (distanceToTurn * distanceToTurn) * ((driversBrakingSkill * sqrt(tyreWear)) / distanceToTurn) + realTargetSpeed(referenceTargetSpeed, mass, downforce);
}


double realTargetSpeed(double referenceTargetSpeed, double mass, double downforce)
{
    // return referenceTargetSpeed + ((1296 / mass) - (referenceTargetSpeed / 100)) * downforce;
    // return referenceTargetSpeed + ((1224 / mass) - (referenceTargetSpeed / 100)) * downforce;
    return referenceTargetSpeed + ((1152 / mass) - (referenceTargetSpeed / 100)) * (downforce / 4);
}


double acceleration(double drag, double tyreWear, double tyreType, double mass, double downforce,
                    double distanceToCarAhead, double speedOfCarAhead, double downforceOfCarAhead, double speed, float wasOvertaken) // TODO: delete `double speed`
{
    // return (23 - (drag - 2 * pow(2 + tyreWear, 2)) - (mass / 360) - (downforce / 4)) / 2 / FPS;
    // return ((23 - (drag - 2 * pow(2 + tyreWear, 2)) - (90 * downforce + mass) / 360) - ((downforce + (2 * (tyreType * tyreType))) / 4) /*+ slipstream(distanceToCarAhead, speedOfCarAhead, downforceOfCarAhead, speed, wasOvertaken)*/) / 2 / FPS;
    return ((23 - (drag - 2 * pow(2 + tyreWear, 2)) - (90 * downforce + mass) / 360) - ((downforce + (2 * (tyreType * tyreType))) / 4)) * slipstreamMultiplier(distanceToCarAhead, speedOfCarAhead, downforceOfCarAhead, wasOvertaken) / 2 / FPS;
}


double maxSpeed(double drag, double mass, double downforce)
{
    // return pow(19 - drag / 2, 2);
    return 250000 / (mass * sqrt(drag / 2)) - downforce;
}


double slipstreamMultiplier(double distanceToCarAhead, double speedOfCarAhead, double downforceOfCarAhead, /*double speed,*/ float wasOvertaken)
{
    // double x = -(sqrt((distanceToCarAhead * distanceToCarAhead) + (speedOfCarAhead * speedOfCarAhead)) / 4) + (speedOfCarAhead / 2);
    // printf("%d, %f, %f, %f, %f\n", wasOvertaken, distanceToCarAhead, speedOfCarAhead, downforceOfCarAhead, speed);
    // printf("a > %f, %f\n", speedOfCarAhead, speed);
    // if (speedOfCarAhead * speed < 0) return 0;
    // printf("b\n");
    // if (distanceToCarAhead < 0) return 1;
    // printf("c\n");
    if (speedOfCarAhead < 90) return 1;
    if (wasOvertaken > 0) return 1 / (wasOvertaken - (wasOvertaken / 1.2) + 1);


    // double x = (-distanceToCarAhead + speedOfCarAhead + ((downforceOfCarAhead * downforceOfCarAhead) / speed)) / 16;
    // printf("slipstream > %f\n", x);
    // if (x > 0) return x / FPS;
    // else return 0;
    // return (1 + (speedOfCarAhead / (100 * (distanceToCarAhead * distanceToCarAhead))));
    return 1 + ((downforceOfCarAhead * speedOfCarAhead) / (100 * distanceToCarAhead) * SLIPSTREAM_EFFECTIVENESS); // 10 - slipstream effectifity
    // double temp1 = 1 + ((downforceOfCarAhead * speedOfCarAhead) / (100 * distanceToCarAhead));

    // printf("downforce [%f], speed [%f], distance [%f] - %f\n", downforceOfCarAhead, speedOfCarAhead, distanceToCarAhead, temp1);

    // return temp1;
}


double handleTyreWear(double tyreWear, int tyreType, double speed, double targetSpeed)
{
    // return max(0.01, tyreWear - ((speed + pow(5 - tyreType, 2)) / (speed * speed)) / FPS);
    return max(0.01, tyreWear - ((speed + pow(8 - tyreType, 2)) / pow(2 * targetSpeed, 2)) / FPS);
}