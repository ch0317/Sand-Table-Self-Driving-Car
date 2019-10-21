/*
  Input Pull-up Serial

  This example demonstrates the use of pinMode(INPUT_PULLUP). It reads a digital
  input on pin 2 and prints the results to the Serial Monitor.

  The circuit:
  - momentary switch attached from pin 2 to ground
  - built-in LED on pin 13

  Unlike pinMode(INPUT), there is no pull-down resistor necessary. An internal
  20K-ohm resistor is pulled to 5V. This configuration causes the input to read
  HIGH when the switch is open, and LOW when it is closed.

  created 14 Mar 2012
  by Scott Fitzgerald

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/InputPullupSerial
*/
int once_flag = 0;
int NSo_red[2] =  {28,29};
int WEo_red[4] =  {30,31,32,33};
int NSo_green[2] =  {34,35};
int WEo_green[4] =  {36,37,38,39};
int NSo_yellow[2] =  {40,41};
int WEo_yellow[4] =  {42,43,44,45};

#define GREEN 0
#define RED 1
#define YELLOW 2

#define LIGHT_ON 1
#define LIGHT_OFF 0

unsigned long send_last_time_1 = 0;

class TrafficLight
{
  public:
    TrafficLight(int *p_green,int *p_red, int *p_yellow, int num, int start_type);
    void light_loop();
    void green(int flag);
    void yellow(int flag);
    void red(int flag);
    unsigned long light_last_time;
    int light_type;
    
   private:
    int switch_time;
    int light_num;
    int *green_pin_array;
    int *yellow_pin_array;
    int *red_pin_array;
};

TrafficLight NS_light(NSo_green, NSo_red, NSo_yellow, 2, GREEN);
TrafficLight WE_light(WEo_green, WEo_red, WEo_yellow, 4, RED);

void setup() {
  //start serial connection
  Serial.begin(115200);
  //configure pin 2 as an input and enable the internal pull-up resistor
  pinMode(14, INPUT);
  for(int i = 28;i <= 45; i++)
  {
    pinMode(i, OUTPUT);
  }
}

void TrafficLight::green(int flag)
{
  for(int i = 0; i < light_num; i++)
  {
    if(flag == LIGHT_ON)
    {
      digitalWrite(green_pin_array[i], LOW);
    }
    else
    {
      digitalWrite(green_pin_array[i], HIGH);
    }
  }
}

void TrafficLight::red(int flag)
{
  for(int i = 0; i < light_num; i++)
  {
    if(flag == LIGHT_ON)
    {
      digitalWrite(red_pin_array[i], LOW);
    }
    else
    {
      digitalWrite(red_pin_array[i], HIGH);
    }
  }
}

void TrafficLight::yellow(int flag)
{
  for(int i = 0; i < light_num; i++)
  {
    if(flag == LIGHT_ON)
    {
      digitalWrite(yellow_pin_array[i], LOW);
    }
    else
    {
      digitalWrite(yellow_pin_array[i], HIGH);
    }
  }
}

void gate_check(int pin)
{
  int sensorVal = digitalRead(pin);
  //print out the value of the pushbutton
  //Serial.println(sensorVal);
  if(sensorVal == HIGH)
  {
    if(abs(millis() - send_last_time_1) > 5000)
    {
      Serial.print("{ \"state\" : ");
      Serial.print( "\"open\"," );
      Serial.print("\"pin\" : ");
      Serial.print(pin);
      Serial.print("}");

    }

    if(abs(millis() - send_last_time_1) > 1000)
    {
      send_last_time_1 = millis();
    }
  }
}

void TrafficLight::light_loop()
{
  switch(light_type)
  {
    case GREEN:
       if(abs(millis() - light_last_time) > 15000)
      {
        yellow(LIGHT_ON);
        green(LIGHT_OFF);
        red(LIGHT_OFF);
        //Serial.println("yellow");
        light_last_time = millis();
        light_type = YELLOW;
      }
      break;
    case RED:
      if(abs(millis() - light_last_time) > 18000)
      {
        //Serial.println("green");
        light_last_time = millis();
        //Serial.println(light_last_time);
        red(LIGHT_OFF);
        green(LIGHT_ON);
        yellow(LIGHT_OFF);
        light_type = GREEN;
      }
      break;
    case YELLOW:
        if(abs(millis() - light_last_time) > 1000)
        {
          if((millis() - light_last_time) % 500 < 250)
            yellow(LIGHT_ON);
          else
            yellow(LIGHT_OFF);
        }
        if(abs(millis() - light_last_time) > 3000)
        {
          //Serial.println("red");
          yellow(LIGHT_OFF);
          red(LIGHT_ON);
          green(LIGHT_OFF);
          light_type = RED;
          light_last_time = millis();
        }
      break;
  }
}

TrafficLight::TrafficLight(int *p_green,int *p_red, int *p_yellow, int num, int start_type)
{
  this->green_pin_array = p_green;
  this->red_pin_array = p_red;
  this->yellow_pin_array = p_yellow;
  this->light_num = num;
  this->light_type = start_type;
  if(start_type == GREEN)
  {
    green(LIGHT_ON);
  }
  else
  {
    red(LIGHT_ON);  
  }
}

void loop() {
  //read the pushbutton value into a variable
  for(int i = 14; i <= 21; i++)
  {
    gate_check(i);
  }

  NS_light.light_loop();
  WE_light.light_loop();
}
