/* $Id: libk8055.c,v 1.7 2008/08/20 17:00:55 mr_brain Exp $
 *
 * This file is part of the libk8055 Library.
 * MODIFIED FOR MODERN LINUX (libusb-1.0 API) - CORRECTED VERSION
 *
 * Original Copyleft (C) 2005 by Sven Lindberg
 * Original Copyright (C) 2007 by Pjetur G. Hjaltason
 */

#include <stdio.h>
#include <string.h>
#include <math.h>
#include <libusb-1.0/libusb.h> // Use the modern libusb-1.0
#include "k8055.h"

// Define constants from original code
#define PACKET_LEN 8
#define K8055_IPID 0x5500
#define VELLEMAN_VENDOR_ID 0x10cf
#define K8055_MAX_DEV 4
#define USB_OUT_EP 0x01 // Endpoint for writing data
#define USB_INP_EP 0x81 // Endpoint for reading data
#define USB_TIMEOUT 200 // Timeout in milliseconds
#define K8055_ERROR -1

// Data offsets in the 8-byte packet
#define DIGITAL_INP_OFFSET 0
#define DIGITAL_OUT_OFFSET 1
#define ANALOG_1_OFFSET 2
#define ANALOG_2_OFFSET 3
#define COUNTER_1_OFFSET 4
#define COUNTER_2_OFFSET 6

// Command codes
#define CMD_RESET 0x00
#define CMD_SET_DEBOUNCE_1 0x01
#define CMD_SET_DEBOUNCE_2 0x02 // Corrected from 0x01 in original
#define CMD_RESET_COUNTER_1 0x03
#define CMD_RESET_COUNTER_2 0x04
#define CMD_SET_ANALOG_DIGITAL 0x05

int DEBUG = 0;

// Structure to hold device state
struct k8055_dev {
    unsigned char data_in[PACKET_LEN];
    unsigned char data_out[PACKET_LEN];
    libusb_device_handle *device_handle; // Modern libusb handle
    int DevNo;
};

static struct k8055_dev k8055d[K8055_MAX_DEV];
static struct k8055_dev *CurrDev;

// Global libusb session context
static libusb_context *usb_ctx = NULL;

static void init_usb(void)
{
    static int Done = 0;
    if (!Done)
    {
        if (libusb_init(&usb_ctx) < 0)
        {
            fprintf(stderr, "Error: Failed to initialize libusb\n");
        }
        Done = 1;
    }
}

static int ReadK8055Data(void)
{
    int read_status = 0, transferred = 0, i;

    if (!CurrDev || !CurrDev->device_handle) return K8055_ERROR;

    for (i = 0; i < 3; i++)
    {
        read_status = libusb_interrupt_transfer(
            CurrDev->device_handle, USB_INP_EP, CurrDev->data_in, PACKET_LEN, &transferred, USB_TIMEOUT);

        if (read_status == 0 && transferred == PACKET_LEN)
        {
            int board_id_from_packet = CurrDev->data_in[1] % 10;
            if (board_id_from_packet == CurrDev->DevNo)
            {
                return 0;
            }
        }
        if (DEBUG) fprintf(stderr, "Read retry (%s)\n", libusb_strerror(read_status));
    }
    return K8055_ERROR;
}

static int WriteK8055Data(unsigned char cmd)
{
    int write_status = 0, transferred = 0, i;

    if (!CurrDev || !CurrDev->device_handle) return K8055_ERROR;

    CurrDev->data_out[0] = cmd;
    for (i = 0; i < 3; i++)
    {
        write_status = libusb_interrupt_transfer(
            CurrDev->device_handle, USB_OUT_EP, CurrDev->data_out, PACKET_LEN, &transferred, USB_TIMEOUT);
        
        if (write_status == 0 && transferred == PACKET_LEN)
        {
            return 0;
        }
        if (DEBUG) fprintf(stderr, "Write retry (%s)\n", libusb_strerror(write_status));
    }
    return K8055_ERROR;
}

int OpenDevice(long BoardAddress)
{
    libusb_device **devs;
    libusb_device_handle *handle = NULL;
    ssize_t cnt;
    int i = 0;
    int ipid;

    if (BoardAddress < 0 || BoardAddress >= K8055_MAX_DEV)
    {
        return K8055_ERROR;
    }
    
    if (k8055d[BoardAddress].device_handle != NULL) {
        SetCurrentDevice(BoardAddress);
        return BoardAddress;
    }

    init_usb();
    ipid = K8055_IPID + (int)BoardAddress;

    cnt = libusb_get_device_list(usb_ctx, &devs);
    if (cnt < 0) return K8055_ERROR;

    for (i = 0; devs[i]; i++)
    {
        struct libusb_device_descriptor desc;
        libusb_get_device_descriptor(devs[i], &desc);

        if (desc.idVendor == VELLEMAN_VENDOR_ID && desc.idProduct == ipid)
        {
            if (libusb_open(devs[i], &handle) == 0)
            {
                if (DEBUG) fprintf(stderr, "Found K8055 at address %ld\n", BoardAddress);

                if (libusb_kernel_driver_active(handle, 0) == 1)
                {
                    if (DEBUG) fprintf(stderr, "Detaching kernel driver...\n");
                    if (libusb_detach_kernel_driver(handle, 0) != 0)
                    {
                        fprintf(stderr, "Error: Could not detach kernel driver.\n");
                        libusb_close(handle);
                        handle = NULL;
                        continue;
                    }
                }

                if (libusb_claim_interface(handle, 0) == 0)
                {
                    CurrDev = &k8055d[BoardAddress];
                    CurrDev->device_handle = handle;
                    CurrDev->DevNo = BoardAddress + 1;
                    SetCurrentDevice(BoardAddress);

                    memset(CurrDev->data_out, 0, PACKET_LEN);
                    WriteK8055Data(CMD_RESET);
                    if (ReadK8055Data() == 0)
                    {
                        libusb_free_device_list(devs, 1);
                        return BoardAddress;
                    }
                    else
                    {
                       fprintf(stderr, "Error: Found device, but failed initial communication.\n");
                       CloseDevice();
                    }
                }
                else
                {
                    fprintf(stderr, "Error: Could not claim interface.\n");
                    libusb_close(handle);
                    handle = NULL;
                }
            }
        }
    }

    libusb_free_device_list(devs, 1);
    if (DEBUG) fprintf(stderr, "Could not find K8055 with address %d\n", (int)BoardAddress);
    return K8055_ERROR;
}

int CloseDevice()
{
    if (!CurrDev || !CurrDev->device_handle)
    {
        if (DEBUG) fprintf(stderr, "Current device is not open\n");
        return 0;
    }
    libusb_release_interface(CurrDev->device_handle, 0);
    libusb_close(CurrDev->device_handle);
    CurrDev->device_handle = NULL;
    CurrDev->DevNo = 0;
    return 0;
}

long SetCurrentDevice(long deviceno)
{
    if (deviceno >= 0 && deviceno < K8055_MAX_DEV)
    {
        if (k8055d[deviceno].device_handle != NULL)
        {
            CurrDev = &k8055d[deviceno];
            return deviceno;
        }
    }
    return K8055_ERROR;
}

long SearchDevices(void)
{
    libusb_device **devs;
    ssize_t cnt;
    int i;
    long retval = 0;

    init_usb();
    cnt = libusb_get_device_list(usb_ctx, &devs);
    if (cnt < 0) return 0;

    for (i = 0; devs[i]; i++)
    {
        struct libusb_device_descriptor desc;
        libusb_get_device_descriptor(devs[i], &desc);

        if (desc.idVendor == VELLEMAN_VENDOR_ID)
        {
            if (desc.idProduct == K8055_IPID + 0) retval |= 0x01;
            if (desc.idProduct == K8055_IPID + 1) retval |= 0x02;
            if (desc.idProduct == K8055_IPID + 2) retval |= 0x04;
            if (desc.idProduct == K8055_IPID + 3) retval |= 0x08;
        }
    }
    libusb_free_device_list(devs, 1);
    return retval;
}

long ReadAnalogChannel(long Channel)
{
    if (Channel != 1 && Channel != 2) return K8055_ERROR;
    if (ReadK8055Data() != 0) return K8055_ERROR;

    return (Channel == 1) ? CurrDev->data_in[ANALOG_1_OFFSET] : CurrDev->data_in[ANALOG_2_OFFSET];
}

int ReadAllAnalog(long *data1, long *data2)
{
    if (ReadK8055Data() != 0) return K8055_ERROR;

    *data1 = CurrDev->data_in[ANALOG_1_OFFSET];
    *data2 = CurrDev->data_in[ANALOG_2_OFFSET];
    return 0;
}

int OutputAnalogChannel(long Channel, long data)
{
    if (Channel != 1 && Channel != 2) return K8055_ERROR;

    if (Channel == 1)
        CurrDev->data_out[ANALOG_1_OFFSET] = (unsigned char)data;
    else
        CurrDev->data_out[ANALOG_2_OFFSET] = (unsigned char)data;
    
    return WriteK8055Data(CMD_SET_ANALOG_DIGITAL);
}

int OutputAllAnalog(long data1, long data2)
{
    CurrDev->data_out[ANALOG_1_OFFSET] = (unsigned char)data1;
    CurrDev->data_out[ANALOG_2_OFFSET] = (unsigned char)data2;
    return WriteK8055Data(CMD_SET_ANALOG_DIGITAL);
}

int WriteAllDigital(long data)
{
    CurrDev->data_out[DIGITAL_OUT_OFFSET] = (unsigned char)data;
    return WriteK8055Data(CMD_SET_ANALOG_DIGITAL);
}

long ReadAllDigital()
{
    if (ReadK8055Data() != 0) return K8055_ERROR;
    
    return (((CurrDev->data_in[0] >> 4) & 0x03) |
            ((CurrDev->data_in[0] << 2) & 0x04) |
            ((CurrDev->data_in[0] >> 3) & 0x18));
}

int ReadAllValues(long *data1, long *data2, long *data3, long *data4, long *data5)
{
    if (ReadK8055Data() != 0) return K8055_ERROR;

    *data1 = ReadAllDigital();
    *data2 = CurrDev->data_in[ANALOG_1_OFFSET];
    *data3 = CurrDev->data_in[ANALOG_2_OFFSET];
    *data4 = CurrDev->data_in[COUNTER_1_OFFSET] | (CurrDev->data_in[COUNTER_1_OFFSET + 1] << 8);
    *data5 = CurrDev->data_in[COUNTER_2_OFFSET] | (CurrDev->data_in[COUNTER_2_OFFSET + 1] << 8);
    return 0;
}

int SetAllValues(int DigitalData, int AdData1, int AdData2)
{
    CurrDev->data_out[DIGITAL_OUT_OFFSET] = (unsigned char)DigitalData;
    CurrDev->data_out[ANALOG_1_OFFSET] = (unsigned char)AdData1;
    CurrDev->data_out[ANALOG_2_OFFSET] = (unsigned char)AdData2;
    return WriteK8055Data(CMD_SET_ANALOG_DIGITAL);
}

int ResetCounter(long CounterNo)
{
    if (CounterNo != 1 && CounterNo != 2) return K8055_ERROR;
    unsigned char cmd = (CounterNo == 1) ? CMD_RESET_COUNTER_1 : CMD_RESET_COUNTER_2;
    return WriteK8055Data(cmd);
}

long ReadCounter(long CounterNo)
{
    if (CounterNo != 1 && CounterNo != 2) return K8055_ERROR;
    if (ReadK8055Data() != 0) return K8055_ERROR;
    
    int offset = (CounterNo == 1) ? COUNTER_1_OFFSET : COUNTER_2_OFFSET;
    return CurrDev->data_in[offset] | (CurrDev->data_in[offset + 1] << 8);
}

int SetCounterDebounceTime(long CounterNo, long DebounceTime)
{
    float value;
    if (CounterNo != 1 && CounterNo != 2) return K8055_ERROR;

    if (DebounceTime > 7450) DebounceTime = 7450;
    if (DebounceTime < 0) DebounceTime = 0;
    
    value = sqrtf(DebounceTime / 0.115f);
    
    unsigned char int_value = (unsigned char)(value + 0.5f);

    if (CounterNo == 1)
    {
        CurrDev->data_out[6] = int_value;
        return WriteK8055Data(CMD_SET_DEBOUNCE_1);
    }
    else
    {
        CurrDev->data_out[7] = int_value;
        return WriteK8055Data(CMD_SET_DEBOUNCE_2);
    }
}

// ===================================================================
//
// The remaining functions are the public API for controlling the board.
//
// ===================================================================

int ClearAllAnalog() { return OutputAllAnalog(0, 0); }
int SetAllAnalog() { return OutputAllAnalog(0xff, 0xff); }
int ClearAllDigital() { return WriteAllDigital(0x00); }
int SetAllDigital() { return WriteAllDigital(0xff); }

// *** THIS IS THE MISSING FUNCTION THAT WAS ADDED BACK ***
int ClearAnalogChannel(long Channel)
{
    if (Channel != 1 && Channel != 2) return K8055_ERROR;
    return OutputAnalogChannel(Channel, 0);
}

int SetAnalogChannel(long Channel)
{
    if (Channel != 1 && Channel != 2) return K8055_ERROR;
    return OutputAnalogChannel(Channel, 0xff);
}

int ClearDigitalChannel(long Channel) {
    if (Channel < 1 || Channel > 8) return K8055_ERROR;
    unsigned char data = CurrDev->data_out[1] & ~(1 << (Channel-1));
    return WriteAllDigital(data);
}

int SetDigitalChannel(long Channel) {
    if (Channel < 1 || Channel > 8) return K8055_ERROR;
    unsigned char data = CurrDev->data_out[1] | (1 << (Channel-1));
    return WriteAllDigital(data);
}

int ReadDigitalChannel(long Channel)
{
    long rval;
    if (Channel < 1 || Channel > 8) return K8055_ERROR; // Original only checked 1-5, but let's be safe
    if ((rval = ReadAllDigital()) == K8055_ERROR) return K8055_ERROR;
    return ((rval & (1 << (Channel - 1))) != 0);
}

char *Version(void)
{
    return (VERSION);
}
