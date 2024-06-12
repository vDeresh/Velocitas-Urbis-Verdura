#include <math.h>
#include <stdio.h>
#include <stdlib.h>
// #include <time.h>
#include <sys/time.h>


void init(float _slipstream_effectiveness);

double handleSpeed(int alreadyTurning, double currentSpeed, double distanceToTurn, double tyreWear, double tyreType, double driversBrakingSkill, double referenceTargetSpeed, double mass, double downforce, double drag, double distanceToCarAhead, double speedOfCarAhead, double downforceOfCarAhead, float wasOvertaken, double ultimateAccelerationMultiplier3000, double maxSpeed, int gear);
double braking(double distanceToTurn, double driversBrakingSkill, double tyreWear, double referenceTargetSpeed, double mass, double downforce);
double realTargetSpeed(double referenceTargetSpeed, double mass, double downforce);
double acceleration(double drag, double tyreWear, double tyreType, double mass, double downforce, double distanceToCarAhead, double speedOfCarAhead, double downforceOfCarAhead, double speed, float wasOvertaken, double ultimateAccelerationMultiplier3000, int gear);
double maxSpeed(double drag, double mass, double downforce);

double slipstreamMultiplier(double distanceToCarAhead, double speedOfCarAhead, double downforceOfCarAhead, /*double currentSpeed,*/ float wasOvertaken);
double dirtyAir(double distanceToCarAhead, double downforceOfCarAhead, double speedOfCarAhead);

double handleTyreWear(double tyreWear, int tyreType, double speed, double targetSpeed);
double tyreEfficiency(int tyreType, double tyreWear);


const int FPS = 120;
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


double _temp_dirty_air;
double _temp_result_speed;

double s1;
double s2;

double result;


float SLIPSTREAM_EFFECTIVENESS;

void init(float _slipstream_effectiveness)
{
    SLIPSTREAM_EFFECTIVENESS = _slipstream_effectiveness;

    gettimeofday(&t1, NULL);
    srand(t1.tv_usec * t1.tv_sec);
}

// TODO
double handleSpeed(int alreadyTurning, double currentSpeed, double distanceToTurn, double tyreWear, double tyreType, double driversBrakingSkill,
                   double referenceTargetSpeed, double mass, double downforce, double drag,
                   double distanceToCarAhead, double speedOfCarAhead, double downforceOfCarAhead, float wasOvertaken,
                   double ultimateAccelerationMultiplier3000,
                   double maxSpeed,
                   int gear)
{
    gettimeofday(&t1, NULL);
    srand(t1.tv_usec * t1.tv_sec);

    currentSpeed *= 2 * FPS;
    speedOfCarAhead *= 2 * FPS;

    if (alreadyTurning) {
        _temp_dirty_air = dirtyAir(distanceToCarAhead, downforceOfCarAhead, speedOfCarAhead);
        _temp_result_speed = min(maxSpeed, (min(realTargetSpeed(referenceTargetSpeed, mass, downforce), currentSpeed + acceleration(drag, tyreWear, tyreType, mass, downforce, distanceToCarAhead, speedOfCarAhead, downforceOfCarAhead, currentSpeed, wasOvertaken, ultimateAccelerationMultiplier3000, gear))));

        if (_temp_result_speed + _temp_dirty_air < 40) return (_temp_result_speed - (rand() % 1001 / 10000)) / 2 / FPS;
        else return (_temp_result_speed + _temp_dirty_air - (rand() % 1001 / 10000)) / 2 / FPS;
    }

    s1 = min(maxSpeed, braking(distanceToTurn, driversBrakingSkill, tyreWear, referenceTargetSpeed, mass, downforce));
    s2 = min(maxSpeed, currentSpeed + acceleration(drag, tyreWear, tyreType, mass, downforce, distanceToCarAhead, speedOfCarAhead, downforceOfCarAhead, currentSpeed, wasOvertaken, ultimateAccelerationMultiplier3000, gear));

    return (min(s1, s2) - (rand() % 1001 / 10000)) / 2 / FPS;
}


double handleQualiSpeed(int alreadyTurning, double currentSpeed, double distanceToTurn, double tyreWear, int tyreType, double driversBrakingSkill,
                        double referenceTargetSpeed, double mass, double downforce, double drag,
                        double ultimateAccelerationMultiplier3000,
                        double maxSpeed,
                        int gear)
{
    gettimeofday(&t1, NULL);
    srand(t1.tv_usec * t1.tv_sec);

    currentSpeed *= 2 * FPS;

    if (alreadyTurning) {
        return (min(maxSpeed, (min(realTargetSpeed(referenceTargetSpeed, mass, downforce), currentSpeed + acceleration(drag, tyreWear, tyreType, mass, downforce, 0, 0, 0, currentSpeed, 0, ultimateAccelerationMultiplier3000, gear)))) - (rand() % 1001 / 10000)) / 2 / FPS;
    }

    s1 = min(maxSpeed, braking(distanceToTurn, driversBrakingSkill, tyreWear, referenceTargetSpeed, mass, downforce));
    s2 = min(maxSpeed, currentSpeed + acceleration(drag, tyreWear, tyreType, mass, downforce, 0, 0, 0, currentSpeed, 0, ultimateAccelerationMultiplier3000, gear));

    return (min(s1, s2) - (rand() % 1001 / 10000)) / 2 / FPS;
}


double braking(double distanceToTurn, double driversBrakingSkill, double tyreWear, double referenceTargetSpeed, double mass, double downforce)
{
    return (distanceToTurn * distanceToTurn) * ((driversBrakingSkill * sqrt(tyreWear)) / distanceToTurn) + realTargetSpeed(referenceTargetSpeed, mass, downforce);
    // return (10 * sqrt(distanceToTurn) * distanceToTurn) * ((driversBrakingSkill * sqrt(tyreWear)) / distanceToTurn) + realTargetSpeed(referenceTargetSpeed, mass, downforce);
}


double realTargetSpeed(double referenceTargetSpeed, double mass, double downforce)
{
    // return referenceTargetSpeed + ((1296 / mass) - (referenceTargetSpeed / 100)) * downforce;
    // return referenceTargetSpeed + ((1224 / mass) - (referenceTargetSpeed / 100)) * downforce;
    // return referenceTargetSpeed + ((1152 / mass) - (referenceTargetSpeed / 100)) * (downforce / 4);
    return referenceTargetSpeed + (1.57079633 * (720 / mass) - (referenceTargetSpeed / 100)) * (downforce / 10);
}


double acceleration(double drag, double tyreWear, double tyreType, double mass, double downforce,
                    double distanceToCarAhead, double speedOfCarAhead, double downforceOfCarAhead, double speed, float wasOvertaken,
                    double ultimateAccelerationMultiplier3000,
                    int gear) // TODO: delete `double speed`
{
    // return (23 - (drag - 2 * pow(2 + tyreWear, 2)) - (mass / 360) - (downforce / 4)) / 2 / FPS;
    // return ((23 - (drag - 2 * pow(2 + tyreWear, 2)) - (90 * downforce + mass) / 360) - ((downforce + (2 * (tyreType * tyreType))) / 4) /*+ slipstream(distanceToCarAhead, speedOfCarAhead, downforceOfCarAhead, speed, wasOvertaken)*/) / 2 / FPS;
    // return ((23 - (drag - 2 * pow(2 + tyreWear, 2)) - (90 * downforce + mass) / 360) - ((downforce + (2 * (tyreType * tyreType))) / 4)) * slipstreamMultiplier(distanceToCarAhead, speedOfCarAhead, downforceOfCarAhead, wasOvertaken) * ultimateAccelerationMultiplier3000 / 2 / FPS;
    // return (50 - (drag - 2 * pow(2 + tyreWear, 2)) - (mass / 100) - ((downforce + (2 * (tyreType * tyreType))) / 4)) * slipstreamMultiplier(distanceToCarAhead, speedOfCarAhead, downforceOfCarAhead, wasOvertaken) * ultimateAccelerationMultiplier3000 / 2 / FPS;
    // double result = ((60 - (tyreType * tyreType)) - ((gear - 1) / 4) + (((drag - (downforce / 2)) - (mass / 100)) / tyreEfficiency(tyreType, tyreWear)));
    result = ((60 - (tyreType * tyreType)) - ((gear - 1) / 4) + (((drag - (downforce / 8)) - (mass / 100)) / tyreEfficiency(tyreType, tyreWear)));

    if (result > 0) return result * slipstreamMultiplier(distanceToCarAhead, speedOfCarAhead, downforceOfCarAhead, wasOvertaken) / 2 / FPS;
    else return 0; // retirement
}

double tyreEfficiency(int tyreType, double tyreWear)
{
    return min(((sqrt((tyreType / 10) + 1) * tyreType + 1) * tyreWear) / (tyreType + 1),  1);
}


double maxSpeed(double drag, double mass, double downforce)
{
    // return pow(19 - drag / 2, 2) - downforce;
    // return 250000 / (mass * sqrt(drag / 2)) - downforce;
    return pow(19 - drag / 2, 2) - (downforce / 8);
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
    if (distanceToCarAhead < 2) return 1;
    // if (distanceToCarAhead > 400) return 1;
    if (speedOfCarAhead < 90) return 1;
    // if (wasOvertaken > 0) return 1 / (wasOvertaken - (wasOvertaken / 1.2) + 1);
    if (wasOvertaken > 0) return 1;


    // double x = (-distanceToCarAhead + speedOfCarAhead + ((downforceOfCarAhead * downforceOfCarAhead) / speed)) / 16;
    // printf("slipstream > %f\n", x);
    // if (x > 0) return x / FPS;
    // else return 0;
    // return (1 + (speedOfCarAhead / (100 * (distanceToCarAhead * distanceToCarAhead))));
    return 1 + ((downforceOfCarAhead * speedOfCarAhead) / (400 * distanceToCarAhead * distanceToCarAhead) * SLIPSTREAM_EFFECTIVENESS);
    // double temp1 = 1 + ((downforceOfCarAhead * speedOfCarAhead) / (100 * distanceToCarAhead));

    // printf("downforce [%f], speed [%f], distance [%f] - %f\n", downforceOfCarAhead, speedOfCarAhead, distanceToCarAhead, temp1);

    // return temp1;
}


double handleTyreWear(double tyreWear, int tyreType, double speed, double targetSpeed)
{
    // return max(0.01, tyreWear - ((speed + pow(5 - tyreType, 2)) / (speed * speed)) / FPS);
    // return max(0.01, tyreWear - ((speed + pow(8 - tyreType, 2)) / pow(2 * targetSpeed, 2)) / FPS);
    return max(0.01, tyreWear - ((speed + pow(8 - tyreType, 3)) / (1000 * targetSpeed)) / FPS);
}


double dirtyAir(double distanceToCarAhead, double downforceOfCarAhead, double speedOfCarAhead)
{
    result = ((distanceToCarAhead - (downforceOfCarAhead / 10)) / 2) - (speedOfCarAhead / 100);

    if (result < 0) return result * ((1 + SLIPSTREAM_EFFECTIVENESS) * (1 + SLIPSTREAM_EFFECTIVENESS)) / FPS;
    else return 0;
}