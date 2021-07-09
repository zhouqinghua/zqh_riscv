#include<SPIMemory.h>

#if defined(ARDUINO_SAMD_ZERO) && defined(SERIAL_PORT_USBVIRTUAL)
// Required for Serial on Zero based boards
#define Serial SERIAL_PORT_USBVIRTUAL
#endif

#if defined (SIMBLEE)
#define BAUD_RATE 57600
#define RANDPIN 1
#else
#define BAUD_RATE 57600
#if defined(ARCH_STM32)
#define RANDPIN PA0
#else
#define RANDPIN A0
#endif
#endif

#define TRUE 1
#define FALSE 0

int8_t SPIPins[4] = {-1, -1, -1, 33};


uint8_t inByte = 0;         // incoming serial byte
#define RECV_DONE 0
#define RECV_ADDR 1
#define RECV_DATA 2
uint8_t recv_state = RECV_DONE;
uint8_t recv_idx = 0;
uint8_t recv_bytes_addr[20];
uint8_t recv_bytes_data[20];
uint8_t check_data_en = 0;

SPIFlash flash;

//ascii string to int
uint32_t my_atoi_16(char *str) {
  int len;
  int char_idx;
  uint32_t resault;
  uint32_t cur_int;
  uint8_t shift_n;
  resault = 0;
  len = strlen(str);
  char_idx = 0;
  for (int i = len - 1; i >= 0; i--) {
    cur_int = 0;
    //end char
    if ((str[i] == '\r') || (str[i] == '\n') || (str[i] == ' ')) {
      //cur_int = 0;
      continue;
    }
    else if ((str[i] >= '0') && (str[i] <= '9')) {
      cur_int = str[i] - '0';
      char_idx++;
    }
    else if ((str[i] >= 'a') && (str[i] <= 'f')) {
      cur_int = str[i] - 'a' + 10;
      char_idx++;
    }
    else if ((str[i] >= 'A') && (str[i] <= 'F')) {
      cur_int = str[i] - 'A' + 10;
      char_idx++;
    }
    //illegal char
    else {
      cur_int = 0;
      resault = 0;
      break;
    }

    shift_n = (char_idx - 1)*4;
    resault = resault + (cur_int << shift_n);
  }
  return resault;
}

void send_back(uint8_t ptr[]) {
  uint8_t len;
  len = strlen(ptr);
  for (int i = 0; i < len; i++) {
    Serial.write(ptr[i]);
  }
}

void setup() {
  // start serial port at 9600 bps and wait for port to open:
  Serial.begin(BAUD_RATE);

  if (flash.error()) {
    Serial.println(flash.error(VERBOSE));
  }
  
  flash.begin();

  if (getID()) {
    Serial.println();
    
    powerDownTest();
    powerUpTest();
  }

  //establishContact();  // send a byte to establish contact until receiver responds
}

void loop() {
  uint32_t addr;
  uint8_t wr_data;
  uint8_t rd_data;
  uint8_t erase_done;

  establishContact();
  
  erase_done = eraseChipTest();
  if (erase_done == 0) {
    Serial.print("eraseChipTest fail!!\n");
    while(1);
  }
  

  //clean recieve buffer
  if (Serial.available() > 0) {
      inByte = Serial.read();
  }

  //indicate host to send flash address and data
  Serial.print("**FLASH INIT DONE**\n");

  //recieve host's check_data_en flag
  while(1) {
    if (Serial.available() <= 0) {
      continue;
    }
    inByte = Serial.read();
    if (inByte == '\n') {
      break;
    }
    else if (inByte == '1'){
      check_data_en = 1;
    }
    else if (inByte == '0') {
      check_data_en = 0;
    }
  }
  
  while(1) {
    if (Serial.available() <= 0) {
      continue;
    }

    // get incoming byte:
    inByte = Serial.read();

    if (recv_state == RECV_DONE) {
      if (inByte == '\n') {
        recv_state = RECV_DONE;
      }
      //address
      else if (inByte == '@') {
        recv_state = RECV_ADDR;
        recv_idx = 0;
      }
      //data
      else {
        recv_state = RECV_DATA;
        recv_bytes_data[0] = inByte;
        recv_idx = 1;
      }
    }
    else if (recv_state == RECV_ADDR) {
      recv_bytes_addr[recv_idx] = inByte;
      recv_idx++;
      if (inByte == '\n') {
        recv_bytes_addr[recv_idx] = 0;
        //addr = 0;
        //sscanf(recv_bytes_addr, "%x\n", &addr);
        addr = my_atoi_16(recv_bytes_addr);
        if (check_data_en) {
          Serial.println(addr, HEX);
        }
        //Serial.println(recv_bytes_addr);
        //send_back(recv_bytes_addr);
        recv_state = RECV_DONE;
      }
    }
    else if (recv_state == RECV_DATA) {
      recv_bytes_data[recv_idx] = inByte;
      recv_idx++;
      if (inByte == '\n') {
        recv_bytes_data[recv_idx] = 0;
        //wr_data = 0;
        //sscanf(recv_bytes_data, "%x\n", &wr_data);
        wr_data = my_atoi_16(recv_bytes_data);
        //Serial.println(wr_data, HEX);
        //send_back(recv_bytes_data);

        //mask high 8 bit bits
        uint32_t offset_addr;
        offset_addr = addr & 0x00ffffff;
        flash.writeByte(offset_addr, wr_data);
        if (check_data_en) {
          rd_data = flash.readByte(offset_addr);
          Serial.println(rd_data, HEX);
        }
        
        recv_state = RECV_DONE;
      }
    }


    

    //Serial.print("get: 0x");
    //Serial.print(inByte, HEX);
    //Serial.write(inByte);
    //Serial.print("\n");

    
    // send sensor values:
    //Serial.print(firstSensor);
    //Serial.print(",");
    //Serial.print(secondSensor);
    //Serial.print(",");
    //Serial.println(thirdSensor);
  }
}

void establishContact() {
  while (Serial.available() <= 0) {
    //Serial.println("0,0,0");   // send an initial string
    //delay(300);
  }
  inByte = Serial.read();//drop this byte
}
