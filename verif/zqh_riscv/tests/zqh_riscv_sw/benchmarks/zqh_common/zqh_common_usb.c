#ifndef __ZQH_COMMON_USB_C
#define __ZQH_COMMON_USB_C

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "util.h"
#include "zqh_common_def.h"
#include "zqh_common_funcs.c"

void usb_host_initial_cfg() {
    printf_zqh("USB_CTRL_VERSION(0) = %8x\n", *USB_CTRL_VERSION(0));
    *USB_CTRL_CONFIG(0) = (*USB_CTRL_CONFIG(0)) | (1 << 2);//host mode
    *USB_CTRL_CONFIG(0) = (*USB_CTRL_CONFIG(0)) & (0xfffffffd);//phy de-reset
    *USB_CTRL_HOST_INTERRUPT_EN(0) = 0;//disable int
    *USB_CTRL_HOST_INTERRUPT_STATUS(0) = 0xfff;
    delay_ms(1000);//wait de reset stalble


    *USB_CTRL_UTMI_HOST_TX_SOF_TIMER(0) = 48000;//48000 is 1ms
    //host config initial frame number
    *USB_CTRL_UTMI_HOST_TX_FRAME_NUM(0) = 0x00;//0x88, 0x1e, 0x3e, 0xfd
    *USB_CTRL_UTMI_HOST_TRANS_TIMEOUT_CNT(0) = 2000;
    //host config sof_en, iso_en, sof_sync
    //*USB_CTRL_UTMI_HOST_CONTROL(0) = (1 << 4) | (0 << 3) | (1 << 1);//sof_en = 1, iso_en = 0, sof_sync = 1
    *USB_CTRL_UTMI_HOST_CONTROL(0) = (1 << 4) | (0 << 3) | (0 << 1);//sof_en = 1, iso_en = 0, sof_sync = 0


    //wait connection
    usb_host_wait_connection();
    printf_zqh("usb host initial connection found\n");


    //host drive usb line to se0 to reset all devices
    usb_host_line_reset();
    usb_host_wait_disconnection();
    printf_zqh("usb host disconnection found\n");
    //wait connection again
    usb_host_wait_connection();
    printf_zqh("usb host 2nd connection found\n");
    if (*USB_CTRL_UTMI_HOST_CONNECT_STATE(0) == 1) {
        printf_zqh("usb speed is FULL\n");
    }
    else if (*USB_CTRL_UTMI_HOST_CONNECT_STATE(0) == 2) {
        printf_zqh("usb speed is LOW\n");
    }


    //host/device phy cfg and enable
    *USB_PHY_CFG2(0) = 0x12;//tx_eop_j_cnt, tx_eop_se0_cnt
    *USB_PHY_CFG0(0) = 0x1;//rx_en
    //host transaction enable
    *USB_CTRL_CONFIG(0) = *USB_CTRL_CONFIG(0) | 0x1;//usb_ctrl transaction en

}


#define USB_REQ_GET_STATUS             0
#define USB_REQ_CLEAR_FEATURE          1
#define USB_REQ_SET_FEATURE            3
#define USB_REQ_SET_ADDRESS            5
#define USB_REQ_GET_DESCRIPTOR         6
#define USB_REQ_SET_DESCRIPTOR         7
#define USB_REQ_GET_CONFIGURATION      8
#define USB_REQ_SET_CONFIGURATION      9
#define USB_REQ_GET_INTERFACE          10
#define USB_REQ_SET_INTERFACE          11
#define USB_REQ_SYNCH_FRAME            12

#define USB_DCP_TYPE_DEVICE        1
#define USB_DCP_TYPE_CONFIGURATION 2
#define USB_DCP_TYPE_STRING        3
#define USB_DCP_TYPE_INTERFACE     4
#define USB_DCP_TYPE_ENDPOINT      5

struct USB_SETUP_PACKET
{
 uint8_t  bmRequestType;
 uint8_t  bRequest;
 uint16_t wValue;
 uint16_t wIndex;
 uint16_t wLength;
}__attribute__((packed));
void display_usb_setup_packet(struct USB_SETUP_PACKET *ptr) {
    printf_zqh("USB_SETUP_PACKET:\n"); 
    printf_zqh("bmRequestType = 0x%02x\n", (*ptr).bmRequestType);
    printf_zqh("bRequest      = 0x%02x\n", (*ptr).bRequest     );
    printf_zqh("wValue        = 0x%04x\n", (*ptr).wValue       );
    printf_zqh("wIndex        = 0x%04x\n", (*ptr).wIndex       );
    printf_zqh("wLength       = 0x%04x\n", (*ptr).wLength      );
}


#define DEVICE_DESCRIPTOR               0x01
#define CONFIGURATION_DESCRIPTOR        0x02
#define STRING_DESCRIPTOR               0x03
#define INTERFACE_DESCRIPTOR            0x04
#define ENDPOINT_DESCRIPTOR             0x05

struct USB_DEVICE_DESCRIPTOR
{
 uint8_t  bLength;                               //
 uint8_t  bDescriptorType;                       //
 uint16_t bcdUSB;                                //
 uint8_t  bDeviceClass;                          //
 uint8_t  bDeviceSubClass;                       //
 uint8_t  bDeviceProtocol;                       //
 uint8_t  bMaxPacketSize0;                       //
 uint16_t idVendor;                              //
 uint16_t idProduct;                             //
 uint16_t bcdDevice;                             //
 uint8_t  iManufacturer;                         //
 uint8_t  iProduct;                              //
 uint8_t  iSerialNumber;                         //
 uint8_t  bNumConfigurations;                    //
}__attribute__((packed));
void display_usb_device_dcescriptor(struct USB_DEVICE_DESCRIPTOR *ptr) {
    printf_zqh("USB_DEVICE_DESCRIPTOR:\n"); 
    printf_zqh("bLength            = 0x%02x\n", (*ptr).bLength           ); 
    printf_zqh("bDescriptorType    = 0x%02x\n", (*ptr).bDescriptorType   ); 
    printf_zqh("bcdUSB             = 0x%04x\n", (*ptr).bcdUSB            ); 
    printf_zqh("bDeviceClass       = 0x%02x\n", (*ptr).bDeviceClass      ); 
    printf_zqh("bDeviceSubClass    = 0x%02x\n", (*ptr).bDeviceSubClass   ); 
    printf_zqh("bDeviceProtocol    = 0x%02x\n", (*ptr).bDeviceProtocol   ); 
    printf_zqh("bMaxPacketSize0    = 0x%02x\n", (*ptr).bMaxPacketSize0   ); 
    printf_zqh("idVendor           = 0x%04x\n", (*ptr).idVendor          ); 
    printf_zqh("idProduct          = 0x%04x\n", (*ptr).idProduct         ); 
    printf_zqh("bcdDevice          = 0x%04x\n", (*ptr).bcdDevice         ); 
    printf_zqh("iManufacturer      = 0x%02x\n", (*ptr).iManufacturer     ); 
    printf_zqh("iProduct           = 0x%02x\n", (*ptr).iProduct          ); 
    printf_zqh("iSerialNumber      = 0x%02x\n", (*ptr).iSerialNumber     ); 
    printf_zqh("bNumConfigurations = 0x%02x\n", (*ptr).bNumConfigurations); 
}


 
struct USB_CONFIGURATION_DESCRIPTOR
{
 uint8_t  bLength;                               //
 uint8_t  bDescriptorType;                       //
 uint16_t wTotalLength;                          //
 uint8_t  bNumInterfaces;                        //
 uint8_t  bConfigurationValue;                   //
 uint8_t  iConfiguration;                        //
 uint8_t  bmAttributes;                          //
 uint8_t  MaxPower;                              //
}__attribute__((packed));
void display_usb_cfg_dcescriptor(struct USB_CONFIGURATION_DESCRIPTOR *ptr) {
    printf_zqh("USB_CONFIGURATION_DESCRIPTOR:\n"); 
    printf_zqh("bLength             = 0x%02x\n", (*ptr).bLength            ); 
    printf_zqh("bDescriptorType     = 0x%02x\n", (*ptr).bDescriptorType    ); 
    printf_zqh("wTotalLength        = 0x%04x\n", (*ptr).wTotalLength       ); 
    printf_zqh("bNumInterfaces      = 0x%02x\n", (*ptr).bNumInterfaces     ); 
    printf_zqh("bConfigurationValue = 0x%02x\n", (*ptr).bConfigurationValue); 
    printf_zqh("iConfiguration      = 0x%02x\n", (*ptr).iConfiguration     ); 
    printf_zqh("bmAttributes        = 0x%02x\n", (*ptr).bmAttributes       ); 
    printf_zqh("MaxPower            = 0x%02x\n", (*ptr).MaxPower           ); 
}


 
struct USB_INTERFACE_DESCRIPTOR
{
 uint8_t bLength;                               //
 uint8_t bDescriptorType;                       //
 uint8_t bInterfaceNumber;                      //
 uint8_t bAlternateSetting;                     //
 uint8_t bNumEndpoints;                         //
 uint8_t bInterfaceClass;                       //
 uint8_t bInterfaceSubClass;                    //
 uint8_t bInterfaceProtocol;                    //
 uint8_t iInterface;                            //
}__attribute__((packed));
void display_usb_itf_dcescriptor(struct USB_INTERFACE_DESCRIPTOR *ptr) {
    printf_zqh("USB_INTERFACE_DESCRIPTOR:\n"); 
    printf_zqh("bLength            = 0x%02x\n", (*ptr).bLength           ); 
    printf_zqh("bDescriptorType    = 0x%02x\n", (*ptr).bDescriptorType   ); 
    printf_zqh("bInterfaceNumber   = 0x%02x\n", (*ptr).bInterfaceNumber  ); 
    printf_zqh("bAlternateSetting  = 0x%02x\n", (*ptr).bAlternateSetting ); 
    printf_zqh("bNumEndpoints      = 0x%02x\n", (*ptr).bNumEndpoints     ); 
    printf_zqh("bInterfaceClass    = 0x%02x\n", (*ptr).bInterfaceClass   ); 
    printf_zqh("bInterfaceSubClass = 0x%02x\n", (*ptr).bInterfaceSubClass); 
    printf_zqh("bInterfaceProtocol = 0x%02x\n", (*ptr).bInterfaceProtocol); 
    printf_zqh("iInterface         = 0x%02x\n", (*ptr).iInterface        ); 
}



struct USB_ENDPOINT_DESCRIPTOR
{
 uint8_t  bLength;                                //
 uint8_t  bDescriptorType;                       //
 uint8_t  bEndpointAddress;                      //
 uint8_t  bmAttributes;                          //
 uint16_t wMaxPacketSize;                        //
 uint8_t  bInterval;                             //
}__attribute__((packed));
void display_usb_ep_dcescriptor(struct USB_ENDPOINT_DESCRIPTOR *ptr) {
    printf_zqh("USB_ENDPOINT_DESCRIPTOR:\n"); 
    printf_zqh("bLength          = 0x%02x\n", (*ptr).bLength         ); 
    printf_zqh("bDescriptorType  = 0x%02x\n", (*ptr).bDescriptorType ); 
    printf_zqh("bEndpointAddress = 0x%02x\n", (*ptr).bEndpointAddress); 
    printf_zqh("bmAttributes     = 0x%02x\n", (*ptr).bmAttributes    ); 
    printf_zqh("wMaxPacketSize   = 0x%04x\n", (*ptr).wMaxPacketSize  ); 
    printf_zqh("bInterval        = 0x%02x\n", (*ptr).bInterval       ); 
}

struct USB_HID_DESCRIPTOR
{
    uint8_t bLength;
    uint8_t bDescriptorType;
    uint16_t bcdHID;
    uint8_t bCountryCode;
    uint8_t bNumDescriptors;
    uint8_t bDescriptorType1;
    uint16_t wDescriptorLength1;
}__attribute__((packed));
void display_usb_hid_dcescriptor(struct USB_HID_DESCRIPTOR *ptr) {
    printf_zqh("USB_HID_DESCRIPTOR:\n"); 
    printf_zqh("bLength            = 0x%02x\n", (*ptr).bLength         ); 
    printf_zqh("bDescriptorType    = 0x%02x\n", (*ptr).bDescriptorType ); 
    printf_zqh("bcdHID             = 0x%04x\n", (*ptr).bcdHID); 
    printf_zqh("bCountryCode       = 0x%02x\n", (*ptr).bCountryCode); 
    printf_zqh("bNumDescriptors    = 0x%02x\n", (*ptr).bNumDescriptors); 
    printf_zqh("bDescriptorType1   = 0x%02x\n", (*ptr).bDescriptorType1); 
    printf_zqh("wDescriptorLength1 = 0x%04x\n", (*ptr).wDescriptorLength1); 
}


struct USB_CBW
{
 uint32_t  dCBWSignature;
 uint32_t  dCBWTag;
 uint32_t  dCBWDataTransferLength;
 uint8_t   bmCBWFlag;
 uint8_t   bCBWLUN;
 uint8_t   bCBWCBLength;
 uint8_t   CBWCB[16];
}__attribute__((packed));
void display_usb_cbw(struct USB_CBW *ptr) {
    printf_zqh("USB_CBW:\n");
    printf_zqh("dCBWSignature          = 0x%08x\n", (*ptr).dCBWSignature         );
    printf_zqh("dCBWTag                = 0x%08x\n", (*ptr).dCBWTag               );
    printf_zqh("dCBWDataTransferLength = 0x%08x\n", (*ptr).dCBWDataTransferLength);
    printf_zqh("bmCBWFlag              = 0x%02x\n", (*ptr).bmCBWFlag             );
    printf_zqh("bCBWLUN                = 0x%02x\n", (*ptr).bCBWLUN               );
    printf_zqh("bCBWCBLength           = 0x%02x\n", (*ptr).bCBWCBLength          );
    //for (int i = 0; i < 16; i++) {
    //    printf_zqh("CBWCB[%0d] = 0x%02x\n", i, (*ptr).CBWCB[i]);
    //}
}

void display_usb_cbw_cbwcb(struct USB_CBW *ptr) {
    for (int i = 0; i < 16; i++) {
        printf_zqh("CBWCB[%0d] = 0x%02x\n", i, (*ptr).CBWCB[i]);
    }
}

struct USB_CSW
{
 uint32_t  dCSWSignature;
 uint32_t  dCSWTag;
 uint32_t  dCSWDataResidue;
 uint8_t   bCSWStatus;
}__attribute__((packed));
void display_usb_csw(struct USB_CSW *ptr) {
    printf_zqh("USB_CSW:\n");
    printf_zqh("dCSWSignature   = %08x\n", (*ptr).dCSWSignature  );
    printf_zqh("dCSWTag         = %08x\n", (*ptr).dCSWTag        );
    printf_zqh("dCSWDataResidue = %08x\n", (*ptr).dCSWDataResidue);
    printf_zqh("bCSWStatus      = %02x\n", (*ptr).bCSWStatus     );
}

#define USB_CBS_SCSI_OPCODE_TEST_UNIT_READY 0x00
#define USB_CBS_SCSI_OPCODE_REQUEST_SENSE 0x03
#define USB_CBS_SCSI_OPCODE_INQUIRY 0x12
#define USB_CBS_SCSI_OPCODE_MODE_SENSE 0x1a
#define USB_CBS_SCSI_OPCODE_START_STOP 0x1b
#define USB_CBS_SCSI_OPCODE_PRV_AL_RM 0x1e
#define USB_CBS_SCSI_OPCODE_READ_FORMAT_CAPACITY 0x23
#define USB_CBS_SCSI_OPCODE_READ_CAPACITY_10 0x25
#define USB_CBS_SCSI_OPCODE_READ_10 0x28
#define USB_CBS_SCSI_OPCODE_WRITE_10 0x2a
struct USB_CBW_SCSI_TEST_UNIT_READY 
{
    uint8_t opcode;
    uint32_t reserved;
    uint8_t control;
}__attribute__((packed));
void display_usb_cbw_scsi_test_unit_ready (struct USB_CBW_SCSI_TEST_UNIT_READY *ptr) {
    printf_zqh("USB_CBW_SCSI_TEST_UNIT_READY:\n");
    printf_zqh("opcode    = 0x%02x\n", (*ptr).opcode   );
    printf_zqh("control   = 0x%02x\n", (*ptr).control  );
}

struct USB_CBW_SCSI_INQUIRY
{
    uint8_t opcode;
    uint8_t evpd;
    uint8_t page_code;
    uint16_t allo_len;
    uint8_t control;
}__attribute__((packed));
void display_usb_cbw_scsi_inquiry(struct USB_CBW_SCSI_INQUIRY *ptr) {
    printf_zqh("USB_CBW_SCSI_INQUIRY:\n");
    printf_zqh("opcode    = 0x%02x\n", (*ptr).opcode   );
    printf_zqh("evpd      = 0x%02x\n", (*ptr).evpd     );
    printf_zqh("page_code = 0x%02x\n", (*ptr).page_code);
    printf_zqh("allo_len  = 0x%04x\n", (*ptr).allo_len );
    printf_zqh("control   = 0x%02x\n", (*ptr).control  );
}

// The standard INQUIRY data shall contain at least 36 bytes
// This is the reduced structure for Mass Storage Devices
struct USB_CBW_SCSI_INQUIRY_DATA
{
  uint8_t peripheral;        // Device Type
  uint8_t rmb;               // Removable Media Bit
  uint8_t version;           // Version Field
  uint8_t resp_data_format;  // Response Data Format
  uint8_t additional_len;    // Additional Length
  uint8_t sccstp;            // SCC Supported (include embedded storage array)
  uint8_t bque;              // Basic Queuing
  uint8_t cmdque;            // Command Queuing
  uint8_t vendor_id[8];
  uint8_t product_id[16];
  uint8_t product_rev[4];
}__attribute__((packed));
void display_usb_cbw_scsi_inquiry_data(struct USB_CBW_SCSI_INQUIRY_DATA *ptr) {
    uint8_t buf[20];
    printf_zqh("USB_CBW_SCSI_INQUIRY_DATA:\n");
    printf_zqh("peripheral       = %02x\n", (*ptr).peripheral      );
    printf_zqh("rmb              = %02x\n", (*ptr).rmb             );
    printf_zqh("version          = %02x\n", (*ptr).version         );
    printf_zqh("resp_data_format = %02x\n", (*ptr).resp_data_format);
    printf_zqh("additional_len   = %02x\n", (*ptr).additional_len  );
    printf_zqh("sccstp           = %02x\n", (*ptr).sccstp          );
    printf_zqh("bque             = %02x\n", (*ptr).bque            );
    printf_zqh("cmdque           = %02x\n", (*ptr).cmdque          );
    for (int i = 0; i < 8; i++) {
        buf[i] = (*ptr).vendor_id[i];
    }
    buf[8] = 0;
    printf_zqh("vendor_id = %s\n", buf);
    for (int i = 0; i < 16; i++) {
        buf[i] = (*ptr).product_id[i];
    }
    buf[16] = 0;
    printf_zqh("product_id = %s\n", buf);
    for (int i = 0; i < 4; i++) {
        buf[i] = (*ptr).product_rev[i];
    }
    buf[4] = 0;
    printf_zqh("product_rev = %s\n", buf);
}

struct USB_CBW_SCSI_READ_CAPACITY_10
{
    uint8_t opcode;
    uint8_t obsolete0;
    uint32_t obsolete1;
    uint16_t reserved;
    uint8_t obsolete2;
    uint8_t control;
}__attribute__((packed));
void display_usb_cbw_scsi_read_capacity_10(struct USB_CBW_SCSI_READ_CAPACITY_10 *ptr) {
    printf_zqh("USB_CBW_SCSI_READ_CAPACITY_10:\n");
    printf_zqh("opcode    = 0x%02x\n", (*ptr).opcode   );
}

struct USB_CBW_SCSI_READ_CAPACITY_10_DATA
{
  uint8_t lba_len[4];//big endian
  uint8_t lb_len[4];//big endian
}__attribute__((packed));
void display_usb_cbw_scsi_read_capacity_10_data(struct USB_CBW_SCSI_READ_CAPACITY_10_DATA *ptr) {
    uint32_t lba_len_le;
    uint32_t lb_len_le;

    //change to little endian
    *(((uint8_t *)(&lba_len_le)) + 0) = (*ptr).lba_len[3];
    *(((uint8_t *)(&lba_len_le)) + 1) = (*ptr).lba_len[2];
    *(((uint8_t *)(&lba_len_le)) + 2) = (*ptr).lba_len[1];
    *(((uint8_t *)(&lba_len_le)) + 3) = (*ptr).lba_len[0];

    *(((uint8_t *)(&lb_len_le)) + 0) = (*ptr).lb_len[3];
    *(((uint8_t *)(&lb_len_le)) + 1) = (*ptr).lb_len[2];
    *(((uint8_t *)(&lb_len_le)) + 2) = (*ptr).lb_len[1];
    *(((uint8_t *)(&lb_len_le)) + 3) = (*ptr).lb_len[0];
    printf_zqh("USB_CBW_SCSI_READ_CAPACITY_10_DATA:\n");
    printf_zqh("lba_len = 0x%08x\n", lba_len_le);
    printf_zqh("lb_len  = 0x%08x\n", lb_len_le);
}

struct USB_CBW_SCSI_MODE_SENSE_6
{
    uint8_t opcode;
    uint8_t dbd;
    uint8_t pc_page_code;
    uint8_t subpage_code;
    uint8_t allo_len;
    uint8_t control;
}__attribute__((packed));
void display_usb_cbw_scsi_mode_sense_6(struct USB_CBW_SCSI_MODE_SENSE_6 *ptr) {
    printf_zqh("USB_CBW_SCSI_MODE_SENSE_6:\n");
    printf_zqh("opcode       = 0x%02x\n", (*ptr).opcode      );
    printf_zqh("dbd          = 0x%02x\n", (*ptr).dbd         );
    printf_zqh("pc_page_code = 0x%02x\n", (*ptr).pc_page_code);
    printf_zqh("subpage_code = 0x%02x\n", (*ptr).subpage_code);
    printf_zqh("allo_len     = 0x%02x\n", (*ptr).allo_len    );
    printf_zqh("control      = 0x%02x\n", (*ptr).control     );
}

struct USB_CBW_SCSI_MODE_SENSE_6_DATA
{
    uint8_t mode_data_len;
    uint8_t medium_type;
    uint8_t device_spec_par;
    uint8_t block_dcp_len;
}__attribute__((packed));
void display_usb_cbw_scsi_mode_sense_6_data(struct USB_CBW_SCSI_MODE_SENSE_6_DATA *ptr) {
    printf_zqh("USB_CBW_SCSI_MODE_SENSE_6_DATA:\n");
    printf_zqh("mode_data_len   = 0x%02x\n", (*ptr).mode_data_len  );
    printf_zqh("medium_type     = 0x%02x\n", (*ptr).medium_type    );
    printf_zqh("device_spec_par = 0x%02x\n", (*ptr).device_spec_par);
    printf_zqh("block_dcp_len   = 0x%02x\n", (*ptr).block_dcp_len  );
}

struct USB_CBW_SCSI_READ_FORMAT_CAPACITY
{
    uint8_t opcode;
    uint8_t lun_h;
    uint32_t reserved0;
    uint8_t reserved1;
    uint16_t allo_len;
    uint8_t control;
}__attribute__((packed));
void display_usb_cbw_scsi_read_format_capacity(struct USB_CBW_SCSI_READ_FORMAT_CAPACITY *ptr) {
    printf_zqh("USB_CBW_SCSI_READ_FORMAT_CAPACITY:\n");
    printf_zqh("opcode   = 0x%02x\n", (*ptr).opcode  );
    printf_zqh("lun_h    = 0x%02x\n", (*ptr).lun_h   );
    printf_zqh("allo_len = 0x%04x\n", (*ptr).allo_len);
    printf_zqh("control  = 0x%02x\n", (*ptr).control );
}

struct USB_CBW_SCSI_PRV_AL_RM
{
    uint8_t opcode;
    uint8_t reserved0;
    uint8_t reserved1;
    uint8_t reserved2;
    uint8_t prevent;
    uint8_t control;
}__attribute__((packed));
void display_usb_cbw_scsi_prv_al_rm(struct USB_CBW_SCSI_PRV_AL_RM *ptr) {
    printf_zqh("USB_CBW_SCSI_PRV_AL_RM:\n");
    printf_zqh("opcode  = 0x%02x\n", (*ptr).opcode);
    printf_zqh("prevent = 0x%02x\n", (*ptr).prevent);
    printf_zqh("control = 0x%02x\n", (*ptr).control);
}

struct USB_CBW_SCSI_START_STOP
{
    uint8_t opcode;
    uint8_t immd;
    uint8_t reserved0;
    uint8_t power_cond_mdf;
    uint8_t power_cond_start;
    uint8_t control;
}__attribute__((packed));
void display_usb_cbw_scsi_start_stop(struct USB_CBW_SCSI_START_STOP *ptr) {
    printf_zqh("USB_CBW_SCSI_START_STOP:\n");
    printf_zqh("opcode           = 0x%02x\n", (*ptr).opcode);
    printf_zqh("power_cond_mdf   = 0x%02x\n", (*ptr).power_cond_mdf);
    printf_zqh("power_cond_start = 0x%02x\n", (*ptr).power_cond_start);
    printf_zqh("control          = 0x%02x\n", (*ptr).control);
}

struct USB_CBW_SCSI_READ_10
{
    uint8_t opcode;
    uint8_t prot_dpo_fua_rarc;
    uint32_t lba;
    uint8_t group_num;
    uint16_t transfer_len;
    uint8_t control;
}__attribute__((packed));
void display_usb_cbw_scsi_read_10(struct USB_CBW_SCSI_READ_10 *ptr) {
    printf_zqh("USB_CBW_SCSI_READ_10:\n");
    printf_zqh("opcode            = 0x%02x\n", (*ptr).opcode           );
    printf_zqh("prot_dpo_fua_rarc = 0x%02x\n", (*ptr).prot_dpo_fua_rarc);
    printf_zqh("lba               = 0x%08x\n", (*ptr).lba              );
    printf_zqh("group_num         = 0x%02x\n", (*ptr).group_num        );
    printf_zqh("transfer_len      = 0x%04x\n", (*ptr).transfer_len     );
    printf_zqh("control           = 0x%02x\n", (*ptr).control          );
}

struct USB_CBW_SCSI_REQUEST_SENSE
{
    uint8_t opcode;
    uint8_t desc;
    uint8_t reserved0;
    uint8_t reserved1;
    uint8_t allo_len;
    uint8_t control;
}__attribute__((packed));

void display_usb_cbw_scsi_request_sense(struct USB_CBW_SCSI_REQUEST_SENSE *ptr) {
    printf_zqh("USB_CBW_SCSI_REQUEST_SENSE:\n");
    printf_zqh("opcode   = 0x%02x\n", (*ptr).opcode);
    printf_zqh("desc     = 0x%02x\n", (*ptr).desc);
    printf_zqh("allo_len = 0x%02x\n", (*ptr).allo_len);
    printf_zqh("control  = 0x%02x\n", (*ptr).control);
}


void usb_dcp_copy(uint8_t *dst_ptr, uint8_t *src_ptr) {
    uint32_t len;
    len = *src_ptr;
    for (int i = 0; i < len; i++) {
        *(dst_ptr + i) = *(src_ptr + i);
    }
}

void usb_setup_pkt_copy(uint8_t *dst_ptr, uint8_t *src_ptr) {
    uint32_t len;
    len = 8;
    for (int i = 0; i < len; i++) {
        *(dst_ptr + i) = *(src_ptr + i);
    }
}

void usb_host_tx_addr_cfg(uint8_t addr, uint8_t ep) {
    *USB_CTRL_UTMI_HOST_TX_ADDR(0) = ((ep & 0x0f) << 8) | (addr & 0x7f);
}

void usb_host_line_reset() {
    *USB_PHY_CFG1(0) = 0x1;
    delay_ms(200);//at least 10ms
    *USB_PHY_CFG1(0) = 0x0;
}

void usb_host_wait_connection() {
    while(1) {
        if ((*USB_CTRL_HOST_INTERRUPT_STATUS(0) & 0x4) != 0) {
            *USB_CTRL_HOST_INTERRUPT_STATUS(0) = 0x4;
            break;
        }
    }
}

void usb_host_wait_disconnection() {
    while(1) {
        if ((*USB_CTRL_HOST_INTERRUPT_STATUS(0) & 0x8) != 0) {
            *USB_CTRL_HOST_INTERRUPT_STATUS(0) = 0x8;
            break;
        }
    }
}

uint32_t usb_host_wait_trans_done() {
    uint32_t rx_status;
    while(1) {
        if ((*USB_CTRL_HOST_INTERRUPT_STATUS(0) & 0x1) != 0) {
            *USB_CTRL_HOST_INTERRUPT_STATUS(0) = 0x1;
            break;
        }
    }
    rx_status = *USB_CTRL_UTMI_HOST_RX_STATUS(0);
    *USB_CTRL_UTMI_HOST_RX_STATUS(0) = 0;//clean status
    return rx_status;
}

void host_rx_status_check(uint32_t status) {
    if (status & 0x01) {
        printf_zqh("host_rx_status has crc_error\n");
        while(1);
    }
    else if (status & 0x02) {
        printf_zqh("host_rx_status has bit_stuff_error\n");
        while(1);
    }
    else if (status & 0x08) {
        printf_zqh("host_rx_status has rx_time_out\n");
        while(1);
    }
    else if (status & 0x10) {
        printf_zqh("host_rx_status has nak_recved\n");
        while(1);
    }
    else if (status & 0x20) {
        printf_zqh("host_rx_status has stall_recved\n");
        while(1);
    }
    else if (status & 0x40) {
        printf_zqh("host_rx_status has ack_recved\n");
    }
}

uint32_t usb_host_read_rx_data(uint8_t *ptr) {
    uint32_t data_count;
    uint8_t cur_byte;
    data_count = *USB_CTRL_HOST_RX_FIFO_DATA_COUNT(0);

    for (int i = 0; i < data_count; i++) {
        //skip pid and crc16
        cur_byte = *USB_CTRL_HOST_RX_FIFO_DATA(0);
        if (ptr != NULL) {
            if ((i > 0) && (i < data_count - 2)) {
                *(ptr + i - 1) = cur_byte;
            }
        }
    }
    if (data_count >= 3) {
        return data_count - 3;
    }
    else {
        return 0;
    }
}

#define USB_HOST_TRANS_SETUP 0
#define USB_HOST_TRANS_IN    1
#define USB_HOST_TRANS_OUT0  2
#define USB_HOST_TRANS_OUT1  3
uint32_t usb_host_trans_data_seq;
uint32_t usb_host_trans_stalled;

void usb_host_issue_trans_setup(uint8_t *ptr) {

    for (int i = 0; i < 8; i++) {
        *USB_CTRL_HOST_TX_FIFO_DATA(0) = *(ptr + i);
    }

    *USB_CTRL_UTMI_HOST_CONTROL(0) = (*USB_CTRL_UTMI_HOST_CONTROL(0) & 0x0ff) | (0 << 10) | (USB_HOST_TRANS_SETUP << 8);//zero out len, trans_type
    *USB_CTRL_UTMI_HOST_CONTROL(0) = *USB_CTRL_UTMI_HOST_CONTROL(0) | 0x1;
}
void usb_host_issue_trans_in() {
    *USB_CTRL_UTMI_HOST_CONTROL(0) = (*USB_CTRL_UTMI_HOST_CONTROL(0) & 0x0ff) | (0 << 10) | (USB_HOST_TRANS_IN << 8);//zero out len, trans_type
    *USB_CTRL_UTMI_HOST_CONTROL(0) = *USB_CTRL_UTMI_HOST_CONTROL(0) | 0x1;
}

void usb_host_issue_trans_out(uint8_t *ptr, uint32_t len, uint32_t data_seq) {
    uint32_t trans_type;
    uint32_t trans_zero_out_len;

    if (usb_host_trans_data_seq == 0) {
        trans_type = USB_HOST_TRANS_OUT0;
    }
    else {
        trans_type = USB_HOST_TRANS_OUT1;
    }

    if (len == 0) {
        trans_zero_out_len = 1;
    }
    else {
        trans_zero_out_len = 0;
        for (int i = 0; i < len; i++) {
            *USB_CTRL_HOST_TX_FIFO_DATA(0) = *(ptr + i);
        }
    }

    *USB_CTRL_UTMI_HOST_CONTROL(0) = (*USB_CTRL_UTMI_HOST_CONTROL(0) & 0x0ff) | (trans_zero_out_len << 10) | (trans_type << 8);//zero out len, trans_type
    *USB_CTRL_UTMI_HOST_CONTROL(0) = *USB_CTRL_UTMI_HOST_CONTROL(0) | 0x1;
}

void usb_host_trans_setup(uint8_t *ptr) {
    uint32_t host_rx_status;
    while(1) {
        usb_host_issue_trans_setup(ptr);
        //host wait transaction finished
        host_rx_status = usb_host_wait_trans_done();
        //tmp host_rx_status_check(host_rx_status);
        if (host_rx_status & 0x10) {
            printf_zqh("host_rx_status has nak_recved\n");
            printf_zqh("issue trans setup again\n");
            delay_ms(1000);
        }
        else if (host_rx_status & 0x08) {
            printf_zqh("host_rx_status has rx_time_out\n");
            printf_zqh("issue trans setup again\n");
            delay_ms(1000);
        }
        else if (host_rx_status & 0x20) {
            printf_zqh("host_rx_status has stall_recved\n");
            usb_host_trans_stalled = 1;
            //while(1);
            break;
        }
        else {
            //setup trans need initial data_seq to 1
            usb_host_trans_data_seq = 1;
            //printf_zqh("host_rx_status ok\n");
            break;
        }
    }
}


void usb_host_trans_bulk_out(uint8_t *ptr, uint32_t len, uint32_t data_seq) {
    uint32_t host_rx_status;
    while(1) {
        usb_host_issue_trans_out(ptr, len, data_seq);
        //host wait transaction finished
        host_rx_status = usb_host_wait_trans_done();
        //tmp host_rx_status_check(host_rx_status);
        if (host_rx_status & 0x10) {
            printf_zqh("host_rx_status has nak_recved\n");
            printf_zqh("issue trans out again\n");
            //delay_ms(1000);
        }
        else if (host_rx_status & 0x08) {
            printf_zqh("host_rx_status has rx_time_out\n");
            printf_zqh("issue trans out again\n");
            //delay_ms(1000);
        }
        else if (host_rx_status & 0x20) {
            printf_zqh("host_rx_status has stall_recved\n");
            usb_host_trans_stalled = 1;
            //while(1);
            //printf_zqh("issue trans out again\n");
            //delay_ms(1000);
            break;
        }
        else {
            //flip data_seq
            //printf_zqh("host_rx_status ok\n");
            usb_host_trans_data_seq = (usb_host_trans_data_seq + 1) & 1;
            break;
        }
    }
}

void usb_host_trans_bulk_in() {
    uint32_t host_rx_status;
    while(1) {
        usb_host_issue_trans_in();
        host_rx_status = usb_host_wait_trans_done();
        if (host_rx_status & 0x10) {
            printf_zqh("host_rx_status has nak_recved\n");
            printf_zqh("issue trans in again\n");
            //delay_ms(1000);
        }
        else if (host_rx_status & 0x08) {
            printf_zqh("host_rx_status has rx_time_out\n");
            printf_zqh("issue trans in again\n");
            //delay_ms(1000);
        }
        else if (host_rx_status & 0x20) {
            printf_zqh("host_rx_status has stall_recved\n");
            usb_host_trans_stalled = 1;
            //while(1);
            //printf_zqh("issue trans in again\n");
            //delay_ms(1000);
            break;
        }
        else if (host_rx_status & 0x01) {
            printf_zqh("host_rx_status has crc_error\n");
            break;
        }
        else {
            //printf_zqh("host_rx_status ok\n");
            break;
        }
    }
}

uint32_t usb_host_control_get_descriptor(struct USB_SETUP_PACKET *cmd, uint8_t *buf_ptr) {
    uint32_t len;
    //setup out trans
    usb_host_trans_setup(cmd);

    //bulk in
    usb_host_trans_bulk_in();

    //read out rx data
    len = usb_host_read_rx_data(buf_ptr);

    //bulk out1 zero len pkt for status
    usb_host_trans_bulk_out(NULL, 0, 1);

    return len;
}

void usb_host_control_set_address(struct USB_SETUP_PACKET *cmd) {
    //setup out trans
    usb_host_trans_setup(cmd);

    //bulk zero len in for status
    usb_host_trans_bulk_in();

    //read out rx data
    usb_host_read_rx_data(NULL);
}

void usb_host_control_set_cfg(struct USB_SETUP_PACKET *cmd) {
    //setup out trans
    usb_host_trans_setup(cmd);

    //bulk zero len in for status
    usb_host_trans_bulk_in();

    //read out rx data
    usb_host_read_rx_data(NULL);
}

void usb_host_control_set_itf(struct USB_SETUP_PACKET *cmd) {
    //setup out trans
    usb_host_trans_setup(cmd);

    //bulk zero len in for status
    usb_host_trans_bulk_in();

    //read out rx data
    usb_host_read_rx_data(NULL);
}

void usb_host_control_clear_feature(struct USB_SETUP_PACKET *cmd) {
    //setup out trans
    usb_host_trans_setup(cmd);

    //bulk zero len in for status
    usb_host_trans_bulk_in();

    //read out rx data
    usb_host_read_rx_data(NULL);
}

void usb_host_control_set_idle(struct USB_SETUP_PACKET *cmd) {
    //setup out trans
    usb_host_trans_setup(cmd);

    //bulk zero len in for status
    usb_host_trans_bulk_in();

    //read out rx data
    usb_host_read_rx_data(NULL);
}

void usb_host_control_set_report(struct USB_SETUP_PACKET *cmd) {
    //setup out trans
    usb_host_trans_setup(cmd);

    //bulk zero len in for status
    usb_host_trans_bulk_in();

    //read out rx data
    usb_host_read_rx_data(NULL);
}

void usb_host_extract_str_dcp(uint8_t *dcp_ptr, uint8_t *buf) {
    for (int i = 2; i < *dcp_ptr; i++) {
        if ((i%2) == 0) {
            *(buf + (i - 2)/2) = *(dcp_ptr+i);
        }
    }
}

void usb_host_cbw_send(struct USB_CBW *cmd, uint8_t data_seq) {
    //bulk out trans
    usb_host_trans_bulk_out(cmd, 31, data_seq);
}

uint32_t usb_host_cbw_data_recv(uint8_t *ptr) {
    uint32_t len;
    //bulk in trans
    usb_host_trans_bulk_in();

    //read out rx data
    len = usb_host_read_rx_data(ptr);
    return len;
}

uint32_t usb_host_csw_recv(uint8_t *ptr) {
    uint32_t len;
    //bulk in trans
    usb_host_trans_bulk_in();

    //read out rx data
    len = usb_host_read_rx_data(ptr);
    return len;
}



uint32_t usb_host_int_in(uint8_t *ptr) {
    uint32_t len;
    //int in trans
    usb_host_trans_bulk_in();

    //read out rx data
    len = usb_host_read_rx_data(ptr);
    return len;
}


struct USB_SETUP_PACKET host_setup_pkt;
uint8_t usb_host_rx_buf[64];
struct USB_DEVICE_DESCRIPTOR host_device_dcp;
struct USB_CONFIGURATION_DESCRIPTOR host_cfg_dcp;
struct USB_INTERFACE_DESCRIPTOR host_itf_dcp[2];
struct USB_HID_DESCRIPTOR host_hid_dcp[2];
struct USB_ENDPOINT_DESCRIPTOR host_ep_dcp_in[2];
struct USB_ENDPOINT_DESCRIPTOR host_ep_dcp_out[2];
uint8_t host_str_dcp[4][64];
int usb_host_emum_common(uint8_t device_addr) {
    //get device descriptor
    host_setup_pkt.bmRequestType = 0x80;
    host_setup_pkt.bRequest = USB_REQ_GET_DESCRIPTOR;
    host_setup_pkt.wValue = (USB_DCP_TYPE_DEVICE << 8) | 0x00;
    host_setup_pkt.wIndex = 0x0000;
    host_setup_pkt.wLength = 0x0012;
    printf_zqh("usb_host_control_get_descriptor device\n");
    usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);
    usb_dcp_copy(&host_device_dcp, usb_host_rx_buf);
    printf_zqh("device descriptor:\n");
    display_usb_device_dcescriptor(&host_device_dcp);


    //bus reset again
    usb_host_line_reset();
    usb_host_wait_disconnection();
    usb_host_wait_connection();
    printf_zqh("usb host 3th connection found\n");


    //set address
    host_setup_pkt.bmRequestType = 0x00;
    host_setup_pkt.bRequest = USB_REQ_SET_ADDRESS;
    host_setup_pkt.wValue = device_addr;
    host_setup_pkt.wIndex = 0x0000;
    host_setup_pkt.wLength = 0x0000;
    usb_host_control_set_address(&host_setup_pkt);
    *USB_CTRL_UTMI_HOST_TX_ADDR(0) = device_addr;
    printf_zqh("usb_host_control_set_address to 0x%02x:\n", device_addr);
    delay_ms(10);


    //get configuration descriptor
    host_setup_pkt.bmRequestType = 0x80;
    host_setup_pkt.bRequest = USB_REQ_GET_DESCRIPTOR;
    host_setup_pkt.wValue = (USB_DCP_TYPE_CONFIGURATION << 8) | 0x00;
    host_setup_pkt.wIndex = 0x0000;
    host_setup_pkt.wLength = 0x0040;
    usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);
    usb_dcp_copy(&host_cfg_dcp, usb_host_rx_buf);
    printf_zqh("configuration descriptor:\n");
    display_usb_cfg_dcescriptor(&host_cfg_dcp);

    //extract interface descriptor
    uint8_t *itf_dcp_ptr;
    uint8_t *ep_dcp_ptr;
    itf_dcp_ptr = usb_host_rx_buf + host_cfg_dcp.bLength;
    for (int i = 0; i < host_cfg_dcp.bNumInterfaces; i++) {
        struct USB_INTERFACE_DESCRIPTOR tmp_itf_dcp;
        usb_dcp_copy(&tmp_itf_dcp, itf_dcp_ptr);
        printf_zqh("interface %0d descriptor:\n", i);
        display_usb_itf_dcescriptor(&tmp_itf_dcp);
        host_itf_dcp[i] = tmp_itf_dcp;

        ep_dcp_ptr = itf_dcp_ptr + tmp_itf_dcp.bLength;

        //extract hid descriptor
        struct USB_HID_DESCRIPTOR tmp_hid_dcp;
        if (tmp_itf_dcp.bInterfaceClass == 0x3) {
            usb_dcp_copy(&tmp_hid_dcp, ep_dcp_ptr);
            display_usb_hid_dcescriptor(&tmp_hid_dcp);
            host_hid_dcp[i] = tmp_hid_dcp;
            ep_dcp_ptr = ep_dcp_ptr + tmp_hid_dcp.bLength;
        }

        //extract endpoint descriptor
        struct USB_ENDPOINT_DESCRIPTOR tmp_ep_dcp;
        for (int j = 0 ; j < tmp_itf_dcp.bNumEndpoints; j++) {
            usb_dcp_copy(&tmp_ep_dcp, ep_dcp_ptr);
            printf_zqh("endpoint %0d descriptor:\n", j);
            display_usb_ep_dcescriptor(&tmp_ep_dcp);
            if ((tmp_ep_dcp.bEndpointAddress & 0x80) == 0) {
                host_ep_dcp_out[i] = tmp_ep_dcp;
            }
            else {
                host_ep_dcp_in[i] = tmp_ep_dcp;
            }
            ep_dcp_ptr = ep_dcp_ptr + tmp_ep_dcp.bLength;
        }
        itf_dcp_ptr = ep_dcp_ptr;
    }


    //get string descriptor of language id
    uint16_t langid;
    host_setup_pkt.bmRequestType = 0x80;
    host_setup_pkt.bRequest = USB_REQ_GET_DESCRIPTOR;
    host_setup_pkt.wValue = (USB_DCP_TYPE_STRING << 8) | 0x00;
    host_setup_pkt.wIndex = 0x0000;
    host_setup_pkt.wLength = 0x0040;
    usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);
    langid = (usb_host_rx_buf[3] << 8) | usb_host_rx_buf[2];
    printf_zqh("string descriptor len = %d\n", usb_host_rx_buf[0]);
    printf_zqh("langid is %04x\n", langid);
    for (int i = 0 ; i < usb_host_rx_buf[0]; i++) {
        host_str_dcp[host_setup_pkt.wValue & 0x00ff][i] = usb_host_rx_buf[i];
    }

    //get string descriptor of device
    char str_buf[64];
    if (host_device_dcp.iManufacturer != 0) {
        host_setup_pkt.bmRequestType = 0x80;
        host_setup_pkt.bRequest = USB_REQ_GET_DESCRIPTOR;
        host_setup_pkt.wValue = (USB_DCP_TYPE_STRING << 8) | host_device_dcp.iManufacturer;
        host_setup_pkt.wIndex = langid;
        host_setup_pkt.wLength = 0x0040;
        usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);
        printf_zqh("string descriptor len = %d\n", usb_host_rx_buf[0]);
        usb_host_extract_str_dcp(usb_host_rx_buf, str_buf);
        str_buf[(usb_host_rx_buf[0] - 2)/2] = 0;
        printf_zqh("string Manufacturer:\n");
        printf_zqh("%s\n",str_buf);
        for (int i = 0 ; i < usb_host_rx_buf[0]; i++) {
            host_str_dcp[host_setup_pkt.wValue & 0x00ff][i] = usb_host_rx_buf[i];
        }
    }

    if (host_device_dcp.iProduct != 0) {
        host_setup_pkt.bmRequestType = 0x80;
        host_setup_pkt.bRequest = USB_REQ_GET_DESCRIPTOR;
        host_setup_pkt.wValue = (USB_DCP_TYPE_STRING << 8) | host_device_dcp.iProduct;
        host_setup_pkt.wIndex = langid;
        host_setup_pkt.wLength = 0x0040;
        usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);
        printf_zqh("string descriptor len = %d\n", usb_host_rx_buf[0]);
        usb_host_extract_str_dcp(usb_host_rx_buf, str_buf);
        str_buf[(usb_host_rx_buf[0] - 2)/2] = 0;
        printf_zqh("string Product:\n");
        printf_zqh("%s\n",str_buf);
        for (int i = 0 ; i < usb_host_rx_buf[0]; i++) {
            host_str_dcp[host_setup_pkt.wValue & 0x00ff][i] = usb_host_rx_buf[i];
        }
    }

    if (host_device_dcp.iSerialNumber != 0) {
        host_setup_pkt.bmRequestType = 0x80;
        host_setup_pkt.bRequest = USB_REQ_GET_DESCRIPTOR;
        host_setup_pkt.wValue = (USB_DCP_TYPE_STRING << 8) | host_device_dcp.iSerialNumber;
        host_setup_pkt.wIndex = langid;
        host_setup_pkt.wLength = 0x0040;
        usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);
        printf_zqh("string descriptor len = %d\n", usb_host_rx_buf[0]);
        usb_host_extract_str_dcp(usb_host_rx_buf, str_buf);
        str_buf[(usb_host_rx_buf[0] - 2)/2] = 0;
        printf_zqh("string SerialNumber:\n");
        printf_zqh("%s\n",str_buf);
        for (int i = 0 ; i < usb_host_rx_buf[0]; i++) {
            host_str_dcp[host_setup_pkt.wValue & 0x00ff][i] = usb_host_rx_buf[i];
        }
    }


    //set configuration      
    host_setup_pkt.bmRequestType = 0x00;
    host_setup_pkt.bRequest = USB_REQ_SET_CONFIGURATION;
    host_setup_pkt.wValue = host_cfg_dcp.bConfigurationValue;
    host_setup_pkt.wIndex = 0x0000;
    host_setup_pkt.wLength = 0x0000;
    usb_host_control_set_cfg(&host_setup_pkt);
    printf_zqh("usb_host_control_set_cfg value 0x%02x:\n", host_cfg_dcp.bConfigurationValue);
    delay_ms(10);
}

int usb_host_mass_store_driver_cfg(){
    //mass storage device
    //set interface
    host_setup_pkt.bmRequestType = 0x01;
    host_setup_pkt.bRequest = USB_REQ_SET_INTERFACE;
    host_setup_pkt.wValue = host_itf_dcp[0].bAlternateSetting;
    host_setup_pkt.wIndex = host_itf_dcp[0].bInterfaceNumber;
    host_setup_pkt.wLength = 0x0000;
    usb_host_control_set_itf(&host_setup_pkt);
    printf_zqh("usb_host_control_set_itf bAlternateSetting = 0x%02x:\n", host_itf_dcp[0].bAlternateSetting);
    printf_zqh("usb_host_control_set_itf bInterfaceNumber = 0x%02x:\n", host_itf_dcp[0].bInterfaceNumber);
    delay_ms(10);
}

int usb_host_hid_driver_cfg() {
    //get HID class report descriptor
    host_setup_pkt.bmRequestType = 0x81;
    host_setup_pkt.bRequest = 0x06;
    host_setup_pkt.wValue = 0x2200;
    host_setup_pkt.wIndex = 0x0000;
    host_setup_pkt.wLength = 0x40;//0x0079
    usb_host_control_get_descriptor(&host_setup_pkt, usb_host_rx_buf);
    printf_zqh("HID class report descriptor:\n");
    for (int i = 0; i < 64; i++) {
        printf_zqh("usb_host_rx_buf[%0d] = %02x\n", i, usb_host_rx_buf[i]);
    }

    //set idle
    host_setup_pkt.bmRequestType = 0x21;
    host_setup_pkt.bRequest = 0x0a;
    host_setup_pkt.wValue = 0x0000;
    host_setup_pkt.wIndex = 0x0000;
    host_setup_pkt.wLength = 0x0000;
    usb_host_control_set_idle(&host_setup_pkt);
    printf_zqh("usb_host_control_set_idle done\n");

    //set report
    host_setup_pkt.bmRequestType = 0x21;
    host_setup_pkt.bRequest = 0x09;
    host_setup_pkt.wValue = 0x0200;
    host_setup_pkt.wIndex = 0x0000;
    host_setup_pkt.wLength = 0x0001;
    usb_host_control_set_report(&host_setup_pkt);
    printf_zqh("usb_host_control_set_report done\n");
}

int usb_host_hid_data_proc(uint8_t device_addr){
    usb_host_trans_data_seq = 0;//initial data_seq to 0
    //int in data
    uint8_t int_rx_buf[8];
    usb_host_tx_addr_cfg(device_addr, host_ep_dcp_in[1].bEndpointAddress);
    while(1) {
        usb_host_int_in(int_rx_buf);
        printf_zqh("usb_host_int_in:\n");
        for (int i = 0; i < 8; i++) {
            printf_zqh("int_rx_buf[%0d] = %02x\n", i, int_rx_buf[i]);
        }
        delay_ms(300);
    }
}

int usb_host_mass_store_data_proc(uint8_t device_addr) {
    usb_host_trans_data_seq = 0;//initial data_seq to 0
    uint8_t ep_out_addr;
    uint8_t ep_in_addr;
    ep_out_addr = host_ep_dcp_out[0].bEndpointAddress & 0x0f;
    ep_in_addr = host_ep_dcp_in[0].bEndpointAddress & 0x0f;
    //send test unit ready scsi cmd
    struct USB_CBW usb_host_cbw;
    struct USB_CSW usb_host_csw;

    //INQUIRY
    usb_host_cbw.dCBWSignature = 0x43425355;
    usb_host_cbw.dCBWTag = 0;
    usb_host_cbw.dCBWDataTransferLength = 0x24;
    usb_host_cbw.bmCBWFlag = 0x80;
    usb_host_cbw.bCBWLUN = 0;
    usb_host_cbw.bCBWCBLength = 6;
    struct USB_CBW_SCSI_INQUIRY cb_inquiry;
    cb_inquiry.opcode = USB_CBS_SCSI_OPCODE_INQUIRY;
    cb_inquiry.evpd = 0;
    cb_inquiry.page_code = 0;
    cb_inquiry.allo_len = 0x2400;//big endian
    cb_inquiry.control = 0;
    for (int i = 0; i < usb_host_cbw.bCBWCBLength; i++) {
        usb_host_cbw.CBWCB[i] = *(((uint8_t *)(&cb_inquiry)) + i);
    }
    display_usb_cbw(&usb_host_cbw);
    display_usb_cbw_scsi_inquiry(&cb_inquiry);
    usb_host_tx_addr_cfg(device_addr, ep_out_addr);
    usb_host_cbw_send(&usb_host_cbw, 0);

    usb_host_tx_addr_cfg(device_addr, ep_in_addr);
    struct USB_CBW_SCSI_INQUIRY_DATA cb_inquiry_data;
    usb_host_cbw_data_recv(&cb_inquiry_data);
    display_usb_cbw_scsi_inquiry_data(&cb_inquiry_data);

    usb_host_tx_addr_cfg(device_addr, ep_in_addr);
    usb_host_csw_recv(&usb_host_csw);
    display_usb_csw(&usb_host_csw);

    //read capacity
    usb_host_cbw.dCBWSignature = 0x43425355;
    usb_host_cbw.dCBWTag = 0;
    usb_host_cbw.dCBWDataTransferLength = 0x08;
    usb_host_cbw.bmCBWFlag = 0x80;
    usb_host_cbw.bCBWLUN = 0;
    usb_host_cbw.bCBWCBLength = 10;
    struct USB_CBW_SCSI_READ_CAPACITY_10 cb_read_capacity_10;
    cb_read_capacity_10.opcode = USB_CBS_SCSI_OPCODE_READ_CAPACITY_10;
    cb_read_capacity_10.obsolete0 = 0;
    cb_read_capacity_10.obsolete1 = 0;
    cb_read_capacity_10.obsolete2 = 0;
    cb_read_capacity_10.control = 0;
    for (int i = 0; i < usb_host_cbw.bCBWCBLength; i++) {
        usb_host_cbw.CBWCB[i] = *(((uint8_t *)(&cb_read_capacity_10)) + i);
    }
    display_usb_cbw(&usb_host_cbw);
    display_usb_cbw_scsi_read_capacity_10(&cb_read_capacity_10);
    usb_host_tx_addr_cfg(device_addr, ep_out_addr);
    usb_host_cbw_send(&usb_host_cbw, 0);

    usb_host_tx_addr_cfg(device_addr, ep_in_addr);
    struct USB_CBW_SCSI_READ_CAPACITY_10_DATA cb_read_capacity_10_data;
    usb_host_cbw_data_recv(&cb_read_capacity_10_data);
    display_usb_cbw_scsi_read_capacity_10_data(&cb_read_capacity_10_data);

    usb_host_tx_addr_cfg(device_addr, ep_in_addr);
    usb_host_csw_recv(&usb_host_csw);
    display_usb_csw(&usb_host_csw);

    //clear feature for stall
    if (usb_host_trans_stalled) {
        host_setup_pkt.bmRequestType = 0x02;//endpoint
        host_setup_pkt.bRequest = USB_REQ_CLEAR_FEATURE;
        host_setup_pkt.wValue = 0;
        host_setup_pkt.wIndex = 0x81;//in ep1
        host_setup_pkt.wLength = 0x0000;
        usb_host_tx_addr_cfg(device_addr, 0);//control ep0
        usb_host_control_clear_feature(&host_setup_pkt);

        host_setup_pkt.bmRequestType = 0x02;//endpoint
        host_setup_pkt.bRequest = USB_REQ_CLEAR_FEATURE;
        host_setup_pkt.wValue = 0;
        host_setup_pkt.wIndex = 0x02;//out ep2
        host_setup_pkt.wLength = 0x0000;
        usb_host_tx_addr_cfg(device_addr, 0);//control ep0
        usb_host_control_clear_feature(&host_setup_pkt);

        usb_host_trans_stalled = 0;

        printf_zqh("usb_host_control_clear_feature\n");
        delay_ms(100);
    }

//tmp    //read capacity 5 times
//tmp    for (int cmd_cnt = 0; cmd_cnt < 5; cmd_cnt++) {
//tmp        delay_ms(1000);
//tmp        printf_zqh("cmd_cnt %0d\n", cmd_cnt);
//tmp        //read capacity
//tmp        usb_host_cbw.dCBWSignature = 0x43425355;
//tmp        usb_host_cbw.dCBWTag = 0;
//tmp        usb_host_cbw.dCBWDataTransferLength = 0x08;
//tmp        usb_host_cbw.bmCBWFlag = 0x80;
//tmp        usb_host_cbw.bCBWLUN = 0;
//tmp        usb_host_cbw.bCBWCBLength = 10;
//tmp        struct USB_CBW_SCSI_READ_CAPACITY_10 cb_read_capacity_10;
//tmp        cb_read_capacity_10.opcode = USB_CBS_SCSI_OPCODE_READ_CAPACITY_10;
//tmp        cb_read_capacity_10.obsolete0 = 0;
//tmp        cb_read_capacity_10.obsolete1 = 0;
//tmp        cb_read_capacity_10.obsolete2 = 0;
//tmp        cb_read_capacity_10.control = 0;
//tmp        for (int i = 0; i < usb_host_cbw.bCBWCBLength; i++) {
//tmp            usb_host_cbw.CBWCB[i] = *(((uint8_t *)(&cb_read_capacity_10)) + i);
//tmp        }
//tmp        display_usb_cbw(&usb_host_cbw);
//tmp        display_usb_cbw_scsi_read_capacity_10(&cb_read_capacity_10);
//tmp        usb_host_tx_addr_cfg(device_addr, ep_out_addr);
//tmp        usb_host_cbw_send(&usb_host_cbw, cmd_cnt & 1);
//tmp
//tmp        usb_host_tx_addr_cfg(device_addr, ep_in_addr);
//tmp        struct USB_CBW_SCSI_READ_CAPACITY_10_DATA cb_read_capacity_10_data;
//tmp        usb_host_cbw_data_recv(&cb_read_capacity_10_data);
//tmp        display_usb_cbw_scsi_read_capacity_10_data(&cb_read_capacity_10_data);
//tmp
//tmp        usb_host_tx_addr_cfg(device_addr, ep_in_addr);
//tmp        usb_host_csw_recv(&usb_host_csw);
//tmp        display_usb_csw(&usb_host_csw);
//tmp    }

//tmp    //test unit ready
//tmp    usb_host_cbw.dCBWSignature = 0x43425355;
//tmp    usb_host_cbw.dCBWTag = 0;
//tmp    usb_host_cbw.dCBWDataTransferLength = 0;
//tmp    usb_host_cbw.bmCBWFlag = 0;
//tmp    usb_host_cbw.bCBWLUN = 0;
//tmp    usb_host_cbw.bCBWCBLength = 6;
//tmp    struct USB_CBW_SCSI_TEST_UNIT_READY cb_test_unit_ready;
//tmp    cb_test_unit_ready.opcode = USB_CBS_SCSI_OPCODE_TEST_UNIT_READY;
//tmp    cb_test_unit_ready.reserved = 0;
//tmp    cb_test_unit_ready.control = 0;
//tmp    for (int i = 0; i < usb_host_cbw.bCBWCBLength; i++) {
//tmp        usb_host_cbw.CBWCB[i] = *(((uint8_t *)(&cb_test_unit_ready)) + i);
//tmp    }
//tmp    display_usb_cbw(&usb_host_cbw);
//tmp    display_usb_cbw_scsi_test_unit_ready(&cb_test_unit_ready);
//tmp    usb_host_tx_addr_cfg(device_addr, ep_out_addr);
//tmp    usb_host_cbw_send(&usb_host_cbw, 0);
//tmp
//tmp    usb_host_tx_addr_cfg(device_addr, ep_in_addr);
//tmp    usb_host_csw_recv(&usb_host_csw);
//tmp    display_usb_csw(&usb_host_csw);
//tmp    //while(1);

    //read 10
    usb_host_cbw.dCBWSignature = 0x43425355;
    usb_host_cbw.dCBWTag = 0;
    usb_host_cbw.dCBWDataTransferLength = 512;
    usb_host_cbw.bmCBWFlag = 0x80;
    usb_host_cbw.bCBWLUN = 0;
    usb_host_cbw.bCBWCBLength = 10;
    struct USB_CBW_SCSI_READ_10 cb_read_10;
    cb_read_10.opcode = USB_CBS_SCSI_OPCODE_READ_10;
    cb_read_10.prot_dpo_fua_rarc = 0;
    cb_read_10.lba = 0x00000000;
    cb_read_10.group_num = 0;
    cb_read_10.transfer_len = 0x0100;
    cb_read_10.control = 0;
    for (int i = 0; i < usb_host_cbw.bCBWCBLength; i++) {
        usb_host_cbw.CBWCB[i] = *(((uint8_t *)(&cb_read_10)) + i);
    }
    display_usb_cbw(&usb_host_cbw);
    display_usb_cbw_scsi_read_10(&cb_read_10);
    usb_host_tx_addr_cfg(device_addr, ep_out_addr);
    usb_host_cbw_send(&usb_host_cbw, 1);

    usb_host_tx_addr_cfg(device_addr, ep_in_addr);
    uint8_t cb_read_10_data[64];
    for (int trans_i = 0; trans_i < 8; trans_i++) {
        uint32_t rx_data_len;
        printf_zqh("trans_i %0d\n", trans_i);
        rx_data_len = usb_host_cbw_data_recv(cb_read_10_data);
        printf_zqh("rx_data_len = %0d\n", rx_data_len);
        for (int i = 0; i < 64; i++) {
            printf_zqh("cb_read_10_data[%0d] = 0x%02x\n", i, cb_read_10_data[i]);
        }
    }

    usb_host_tx_addr_cfg(device_addr, ep_in_addr);
    usb_host_csw_recv(&usb_host_csw);
    display_usb_csw(&usb_host_csw);
    while(1);
}

void usb_host_test() {
    usb_host_initial_cfg();

    uint8_t usb_device_addr;
    usb_device_addr = 0x5a;
    usb_host_emum_common(usb_device_addr);

    //hid cfg
//tmp    usb_host_hid_driver_cfg();
//tmp    usb_host_hid_data_proc(usb_device_addr);

    usb_host_mass_store_driver_cfg();
    usb_host_mass_store_data_proc(usb_device_addr);

//tmp    //
//tmp    //clear feature for stall
//tmp    host_setup_pkt.bmRequestType = 0x02;//endpoint
//tmp    host_setup_pkt.bRequest = USB_REQ_CLEAR_FEATURE;
//tmp    host_setup_pkt.wValue = 0;
//tmp    host_setup_pkt.wIndex = 0x81;//in ep1
//tmp    host_setup_pkt.wLength = 0x0000;
//tmp    usb_host_tx_addr_cfg(usb_device_addr, 0);//control ep0
//tmp    usb_host_control_clear_feature(&host_setup_pkt);
//tmp
//tmp    host_setup_pkt.bmRequestType = 0x02;//endpoint
//tmp    host_setup_pkt.bRequest = USB_REQ_CLEAR_FEATURE;
//tmp    host_setup_pkt.wValue = 0;
//tmp    host_setup_pkt.wIndex = 0x02;//out ep2
//tmp    host_setup_pkt.wLength = 0x0000;
//tmp    usb_host_tx_addr_cfg(usb_device_addr, 0);//control ep0
//tmp    usb_host_control_clear_feature(&host_setup_pkt);
//tmp
//tmp    printf_zqh("usb_host_control_clear_feature\n");
//tmp    delay_ms(1000);
//tmp
//tmp    //request sense
//tmp    *USB_CTRL_HOST_RX_FIFO_CONTROL(0) = 1;//flush rx fifo
//tmp    delay_ms(10);
//tmp    usb_host_cbw.dCBWSignature = 0x43425355;
//tmp    usb_host_cbw.dCBWTag = 0;
//tmp    usb_host_cbw.dCBWDataTransferLength = 252;
//tmp    usb_host_cbw.bmCBWFlag = 0x80;
//tmp    usb_host_cbw.bCBWLUN = 0;
//tmp    usb_host_cbw.bCBWCBLength = 6;
//tmp    struct USB_CBW_SCSI_REQUEST_SENSE cb_req_sense;
//tmp    cb_req_sense.opcode = USB_CBS_SCSI_OPCODE_REQUEST_SENSE;
//tmp    cb_req_sense.desc = 0;
//tmp    cb_req_sense.allo_len = 252;
//tmp    cb_req_sense.control = 0;
//tmp    for (int i = 0; i < usb_host_cbw.bCBWCBLength; i++) {
//tmp        usb_host_cbw.CBWCB[i] = *(((uint8_t *)(&cb_req_sense)) + i);
//tmp    }
//tmp    display_usb_cbw(&usb_host_cbw);
//tmp    display_usb_cbw_scsi_request_sense(&cb_req_sense);
//tmp    usb_host_tx_addr_cfg(usb_device_addr, ep_out_addr);
//tmp    usb_host_cbw_send(&usb_host_cbw, 1);
//tmp
//tmp    usb_host_tx_addr_cfg(usb_device_addr, ep_in_addr);
//tmp    uint8_t cb_req_sense_data[64];
//tmp    usb_host_cbw_data_recv(cb_req_sense_data);
//tmp    for (int i = 0; i < 64; i++) {
//tmp        printf_zqh("cb_req_sense_data[%0d] = 0x%02x\n", i, cb_req_sense_data[i]);
//tmp    }
//tmp
//tmp    usb_host_tx_addr_cfg(usb_device_addr, ep_in_addr);
//tmp    usb_host_csw_recv(&usb_host_csw);
//tmp    display_usb_csw(&usb_host_csw);
//tmp    while(1);


//tmp    //request sense
//tmp    usb_host_cbw.dCBWSignature = 0x43425355;
//tmp    usb_host_cbw.dCBWTag = 0;
//tmp    usb_host_cbw.dCBWDataTransferLength = 0x20;
//tmp    usb_host_cbw.bmCBWFlag = 0x80;
//tmp    usb_host_cbw.bCBWLUN = 0;
//tmp    usb_host_cbw.bCBWCBLength = 6;
//tmp    struct USB_CBW_SCSI_REQUEST_SENSE cb_req_sense;
//tmp    cb_req_sense.opcode = USB_CBS_SCSI_OPCODE_REQUEST_SENSE;
//tmp    cb_req_sense.desc = 0;
//tmp    cb_req_sense.allo_len = 0x20;
//tmp    cb_req_sense.control = 0;
//tmp    for (int i = 0; i < usb_host_cbw.bCBWCBLength; i++) {
//tmp        usb_host_cbw.CBWCB[i] = *(((uint8_t *)(&cb_req_sense)) + i);
//tmp    }
//tmp    display_usb_cbw(&usb_host_cbw);
//tmp    display_usb_cbw_scsi_request_sense(&cb_req_sense);
//tmp    usb_host_tx_addr_cfg(usb_device_addr, ep_out_addr);
//tmp    usb_host_cbw_send(&usb_host_cbw, 1);
//tmp
//tmp    usb_host_tx_addr_cfg(usb_device_addr, ep_in_addr);
//tmp    uint8_t cb_req_sense_data[64];
//tmp    usb_host_cbw_data_recv(cb_req_sense_data);
//tmp    for (int i = 0; i < 64; i++) {
//tmp        printf_zqh("cb_req_sense_data[%0d] = 0x%02x\n", i, cb_req_sense_data[i]);
//tmp    }
//tmp
//tmp    usb_host_tx_addr_cfg(usb_device_addr, ep_in_addr);
//tmp    usb_host_csw_recv(&usb_host_csw);
//tmp    display_usb_csw(&usb_host_csw);
//tmp    while(1);
}


uint32_t usb_device_read_rx_data(uint8_t ep, uint8_t *ptr) {
    uint32_t data_count;
    uint8_t cur_byte;
    data_count = *USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,ep);
    for (int i = 0; i < data_count; i++) {
        //skip pid and crc16
        cur_byte = *USB_CTRL_DEVICE_RX_FIFO_DATA(1,ep);
        if ((i > 0) && (i < data_count - 2)) {
            *(ptr + i - 1) = cur_byte;
        }
    }
    if (data_count >= 3) {
        return data_count - 3;
    }
    else {
        return 0;
    }
}

//pop and drop some byte data from rx fifo
//such as zero trans pkt's 3 byte data
void usb_device_drop_rx_data(uint32_t cnt, uint8_t *buf) {
    uint8_t cur_byte;
    uint32_t data_count;
    data_count = *USB_CTRL_DEVICE_RX_FIFO_DATA_COUNT(1,0);
    if (cnt <= data_count) {
        data_count = cnt;
    }
    for (int i = 0; i < data_count; i++) {
        cur_byte = *USB_CTRL_DEVICE_RX_FIFO_DATA(1,0);
        if (buf != NULL) {
             *(buf + i) = cur_byte;
        }
    }
}

uint32_t usb_device_read_int_status() {
    uint32_t status;
    status = *USB_CTRL_DEVICE_INTERRUPT_STATUS(1);
    //stalled
    if ((status & 0x020) != 0) {
        //clean int
        *USB_CTRL_DEVICE_INTERRUPT_STATUS(1) = 0x20;
    }
    //reset event
    else if ((status & 0x004) != 0) {
        //clean int
        *USB_CTRL_DEVICE_INTERRUPT_STATUS(1) = 0x04;
    }
    //trans done
    else if ((status & 0x001) != 0) {
        //clean int
        *USB_CTRL_DEVICE_INTERRUPT_STATUS(1) = 0x1;
    }
    //nacked
    else if ((status & 0x010) != 0) {
        //clean int
        *USB_CTRL_DEVICE_INTERRUPT_STATUS(1) = 0x10;
    }
    //sof_recv
    else if ((status & 0x008) != 0) {
        //clean int
        *USB_CTRL_DEVICE_INTERRUPT_STATUS(1) = 0x08;
    }

    return status;
}

void usb_device_wait_reset_event() {
    while(1) {
        if ((*USB_CTRL_DEVICE_INTERRUPT_STATUS(1) & 0x4) != 0) {
            //clean int
            *USB_CTRL_DEVICE_INTERRUPT_STATUS(1) = 0x4;
            break;
        }
    }
}

int usb_device_wait_done(uint32_t ep) {
    int ret_v;
    while(1) {
        if ((*USB_CTRL_DEVICE_INTERRUPT_STATUS(1) & 0x1) != 0) {
            //clean int
            *USB_CTRL_DEVICE_INTERRUPT_STATUS(1) = 0x1;
            ret_v = 0;
            break;
        }
        else if ((*USB_CTRL_DEVICE_INTERRUPT_STATUS(1) & 0x10) != 0) {
            //clean int
            *USB_CTRL_DEVICE_INTERRUPT_STATUS(1) = 0x10;
            ret_v = 1;//naked
            break;
        }
        else if ((*USB_CTRL_DEVICE_INTERRUPT_STATUS(1) & 0x20) != 0) {
            //clean int
            *USB_CTRL_DEVICE_INTERRUPT_STATUS(1) = 0x20;
            ret_v = 2;//stalled
            break;
        }
        else if ((*USB_CTRL_DEVICE_INTERRUPT_STATUS(1) & 0x04) != 0) {
            //clean int
            *USB_CTRL_DEVICE_INTERRUPT_STATUS(1) = 0x04;
            ret_v = 3;//reset event
            break;
        }
    }
    return ret_v;
}
void usb_device_wait_stall_sent(uint32_t ep) {
    while(1) {
        if ((*USB_CTRL_DEVICE_INTERRUPT_STATUS(1) & 0x20) != 0) {
            //clean int
            *USB_CTRL_DEVICE_INTERRUPT_STATUS(1) = 0x20;
            //clean status
            *USB_CTRL_UTMI_DEVICE_STATUS(1, ep) = 0x00;
            break;
        }
    }
}

void usb_device_ready_trans(uint32_t ep, uint32_t data_id, uint8_t *ptr, uint32_t len) {
    //in trans need set data id and data_zero_len
    uint8_t data_zero_len;
    if (len == 0) {
        data_zero_len = 1;
    }
    else {
        for (int i = 0; i < len; i++) {
            *USB_CTRL_DEVICE_TX_FIFO_DATA(1,ep) = *(ptr + i);
        }
        data_zero_len = 0;
    }
    *USB_CTRL_UTMI_DEVICE_CONTROL(1,ep) = (*USB_CTRL_UTMI_DEVICE_CONTROL(1,ep) & 0xfff3) | (data_zero_len << 3) | (data_id << 2);//data zero len,data_id
    //set ready
    *USB_CTRL_UTMI_DEVICE_CONTROL(1,ep) = *USB_CTRL_UTMI_DEVICE_CONTROL(1,ep) | (1 << 1);
}

void usb_device_rx_data_ready(uint32_t ep) {
    usb_device_ready_trans(ep, 0, NULL, 0);
}

uint32_t usb_device_rx_data_wait(uint32_t ep) {
    uint32_t int_status;
    uint32_t device_status;
    usb_device_rx_data_ready(ep);

    //wait for host's OUT trans
    while(1) {
        int_status = usb_device_read_int_status();
        device_status = *USB_CTRL_UTMI_DEVICE_STATUS(1, ep);
        if ((int_status & 0x20) != 0) {
            printf_zqh("OUT trans status stall_sent\n");
            while(1);
        }
        else if ((int_status & 0x04) != 0) {
            printf_zqh("OUT trans reset event found\n");
            while(1);
        }
        else if ((int_status & 0x01) != 0) {
            //printf_zqh("OUT trans done\n");
            if ((device_status & 0x0008) != 0) {
                //usb_device_ready_trans(ep, data_seq, buf_ptr, pkt_len);
                printf_zqh("OUT trans timeout\n");
                while(1);
                //continue;
                //break;
            }
            break;
        }
        //nak_sent
        else if ((int_status & 0x10) != 0) {
            continue;
        }
        //sof_recv
        else if ((int_status & 0x08) != 0) {
            continue;
        }
        else {
            continue;
        }
    }

    //return int_status;
    *USB_CTRL_UTMI_DEVICE_STATUS(1, ep) = 0;
    return device_status;
}

uint32_t usb_device_trans_data_seq;
uint32_t usb_device_tx_data_wait(uint32_t ep, uint32_t data_seq, uint8_t *buf_ptr, uint32_t pkt_len) {
    uint32_t int_status;
    uint32_t device_status;
    //push data to ep's tx data fifo and set ready
    usb_device_ready_trans(ep, data_seq, buf_ptr, pkt_len);

    //wait for host's IN trans
    while(1) {
        int_status = usb_device_read_int_status();
        device_status = *USB_CTRL_UTMI_DEVICE_STATUS(1, ep);
        if ((int_status & 0x20) != 0) {
            printf_zqh("IN trans status stall_sent\n");
            while(1);
        }
        else if ((int_status & 0x04) != 0) {
            printf_zqh("IN trans reset event found\n");
            while(1);
        }
        else if ((int_status & 0x01) != 0) {
            //check if timeout happen
            //*USB_CTRL_UTMI_DEVICE_STATUS(1, ep) = 0;
            if ((device_status & 0x0008) != 0) {
                //usb_device_ready_trans(ep, data_seq, buf_ptr, pkt_len);
                printf_zqh("IN trans timeout\n");
                //while(1);
                //continue;
                break;
            }
            else {
                //printf_zqh("IN trans done\n");
                break;
            }
        }
        //nak_sent
        else if ((int_status & 0x10) != 0) {
            continue;
        }
        //sof_recv
        else if ((int_status & 0x08) != 0) {
            continue;
        }
        else {
            continue;
        }
    }

    //return int_status;
    *USB_CTRL_UTMI_DEVICE_STATUS(1, ep) = 0;
    return device_status;
}




void usb_device_initial_cfg() {
    printf_zqh("USB_CTRL_VERSION(1) = %8x\n", *USB_CTRL_VERSION(1));
    *USB_CTRL_CONFIG(1) = (*USB_CTRL_CONFIG(1)) | (0 << 2);//device mode
    *USB_CTRL_CONFIG(1) = (*USB_CTRL_CONFIG(1)) & (0xfffffffd);//phy de-reset
    *USB_CTRL_DEVICE_INTERRUPT_EN(1) = 0;//disable int
    *USB_CTRL_DEVICE_INTERRUPT_STATUS(1) = 0xfff;//clean int
    delay_zqh(100);//wait de reset stalble


    usb_device_wait_reset_event();

    *USB_PHY_CFG0(1) = 0x1;//rx_en
    //delay_zqh(100);

    //device config ep0: iso_en, enable
    *USB_CTRL_UTMI_DEVICE_CONTROL(1,0) = (0 << 5) | (1 << 0);//iso_en = 0, enable
    *USB_CTRL_UTMI_DEVICE_CONTROL(1,1) = (0 << 5) | (1 << 0);//iso_en = 0, enable
    *USB_CTRL_UTMI_DEVICE_CONTROL(1,2) = (0 << 5) | (1 << 0);//iso_en = 0, enable

    *USB_CTRL_UTMI_DEVICE_TRANS_TIMEOUT_CNT(1) = 2000;
    
    //device transaction enable
    *USB_CTRL_CONFIG(1) = *USB_CTRL_CONFIG(1) | 0x1;//usb_ctrl transaction en

    //ep0 ready for recieve setup pkt
    usb_device_ready_trans(0, 0, NULL, 0);
    printf_zqh("usb device reset event found\n");
}
#endif
