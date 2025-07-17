#include <PID_v1.h>
// sudo minicom -b 115200 -D /dev/ttyUSB0


#define left_L298_enA 13
#define left_L298_in1 12
#define left_L298_in2 11
#define left_encoder_phaseA 18
#define left_encoder_phaseB 19

#define right_L298_in1 10
#define right_L298_in2 9
#define right_L298_enA 8
#define right_encoder_phaseA 20
#define right_encoder_phaseB 21

#define GEAR_RATIO 21.3
#define ENCODER_PULSE_PER_REV_MOTOR 11.0
#define ENCODER_PULSE_PER_REV_OUTPUT (ENCODER_PULSE_PER_REV_MOTOR * GEAR_RATIO)
#define RAD_PER_SECONDS (2 * PI / 60.0)

unsigned int left_encoder_counter = 0;
unsigned int right_encoder_counter = 0;
String left_encoder_sign = "p";
String right_encoder_sign = "p";

char value[] = "00.00";
uint8_t value_idx = 0;

bool is_cmd_complete = false;
bool is_right_wheel_forward = true;
bool is_left_wheel_forward = true;
bool is_right_wheel_cmd = false;
bool is_left_wheel_cmd = false;

double right_wheel_meas_vel = 0.0;
double left_wheel_meas_vel = 0.0;
double right_wheel_cmd_vel = 0.0;
double left_wheel_cmd_vel = 0.0;
double right_wheel_cmd = 0.0;
double left_wheel_cmd = 0.0;

unsigned long last_millis = 0;
const unsigned long interval = 100;

double Kp_r = 18, Ki_r = 8.3, Kd_r = 0.1;
double Kp_l = 18, Ki_l = 7.5, Kd_l = 0.1;

PID rightMotor(&right_wheel_meas_vel, &right_wheel_cmd, &right_wheel_cmd_vel, Kp_r, Ki_r, Kd_r, DIRECT);
PID leftMotor(&left_wheel_meas_vel, &left_wheel_cmd, &left_wheel_cmd_vel, Kp_l, Ki_l, Kd_l, DIRECT);

int counter = 0.0;


void setup() {
  Serial.begin(115200);
  pinMode(left_L298_enA, OUTPUT);
  pinMode(left_L298_in1, OUTPUT);
  pinMode(left_L298_in2, OUTPUT);
  pinMode(right_L298_enA, OUTPUT);
  pinMode(right_L298_in1, OUTPUT);
  pinMode(right_L298_in2, OUTPUT);
  pinMode(2, OUTPUT);

  digitalWrite(left_L298_in1, HIGH);
  digitalWrite(left_L298_in2, LOW);
  digitalWrite(right_L298_in1, HIGH);
  digitalWrite(right_L298_in2, LOW);

  pinMode(left_encoder_phaseA, INPUT);
  pinMode(left_encoder_phaseB, INPUT);
  pinMode(right_encoder_phaseA, INPUT);
  pinMode(right_encoder_phaseB, INPUT);

  attachInterrupt(digitalPinToInterrupt(left_encoder_phaseA), leftEncoderCallback, RISING);
  attachInterrupt(digitalPinToInterrupt(right_encoder_phaseA), rightEncoderCallback, RISING);

  rightMotor.SetMode(AUTOMATIC);
  leftMotor.SetMode(AUTOMATIC);
  Serial.println("ready");  // 👈 báo cho ROS biết Arduino đã sẵn sàng
}

void loop() {
  if (Serial.available()) {
    char chr = Serial.read();
    //Serial.println(chr);
    if (chr == 'r') {
      is_right_wheel_cmd = true;
      is_left_wheel_cmd = false;
      value_idx = 0;
      is_cmd_complete = false;
      digitalWrite(2, HIGH);
    } else if (chr == 'l') {
      is_right_wheel_cmd = false;
      is_left_wheel_cmd = true;
      value_idx = 0;
    } else if (chr == 'p') {
      updateDirection(true);
    } else if (chr == 'n') {
      updateDirection(false);
    } else if (chr == ',') {
      if (is_right_wheel_cmd)
        right_wheel_cmd_vel = atof(value);
      else if (is_left_wheel_cmd) {
        left_wheel_cmd_vel = atof(value);
        is_cmd_complete = true;
      }

      value_idx = 0;
    } else {
      if (value_idx < 5) {
        value[value_idx++] = chr;
      }
    }
  }

  unsigned long current_millis = millis();
  if (current_millis - last_millis >= interval) {
    right_wheel_meas_vel = 10 * (right_encoder_counter * (60.0 / ENCODER_PULSE_PER_REV_OUTPUT) * RAD_PER_SECONDS);
    left_wheel_meas_vel = 10 * (left_encoder_counter * (60.0 / ENCODER_PULSE_PER_REV_OUTPUT) * RAD_PER_SECONDS);

    rightMotor.Compute();
    leftMotor.Compute();

    if (right_wheel_cmd_vel == 0.0) right_wheel_cmd = 0.0;
    if (left_wheel_cmd_vel == 0.0) left_wheel_cmd = 0.0;

    analogWrite(left_L298_enA, left_wheel_cmd);
    analogWrite(right_L298_enA, right_wheel_cmd);

    //String encoder_read = "r" + right_encoder_sign + String(right_wheel_meas_vel) + ",l" + left_encoder_sign + String(left_wheel_meas_vel) + ",";
    //Serial.println(encoder_read);
    right_encoder_counter = 0;
    left_encoder_counter = 0;
    last_millis = current_millis;
  }
}

void updateDirection(bool forward) {
  if (is_right_wheel_cmd && is_right_wheel_forward != forward) {
    digitalWrite(right_L298_in1, HIGH - digitalRead(right_L298_in1));
    digitalWrite(right_L298_in2, HIGH - digitalRead(right_L298_in2));
    is_right_wheel_forward = forward;
  } else if (is_left_wheel_cmd && is_left_wheel_forward != forward) {
    digitalWrite(left_L298_in1, HIGH - digitalRead(left_L298_in1));
    digitalWrite(left_L298_in2, HIGH - digitalRead(left_L298_in2));
    is_left_wheel_forward = forward;
  }
}

void leftEncoderCallback() {
  left_encoder_counter++;
  left_encoder_sign = digitalRead(left_encoder_phaseB) ? "p" : "n";
}

void rightEncoderCallback() {
  right_encoder_counter++;
  right_encoder_sign = digitalRead(right_encoder_phaseB) ? "p" : "n";
}
