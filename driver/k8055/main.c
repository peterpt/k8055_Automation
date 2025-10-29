/* $Id: main.c,v 1.3 2007/03/15 14:37:58 pjetur Exp $
 ***************************************************************************
 *   Copyright (C) 2004 by Nicolas Sutre                                   *
 *   nicolas.sutre@free.fr                                                 *
 *                                                                         *
 *   Copyright (C) 2005 by Bob Dempsey                                     *
 *   bdempsey_64@msn.com 						   *
 *									   *
 *   Copyright (C) 2005 by Julien Etelain and Edward Nys		   *
 *   Converted to C							   *
 *   Commented and improved by Julien Etelain <julien.etelain@utbm.fr>     *
 *                             Edward Nys <edward.ny@utbm.fr>              *
 *                                                                         *
 *   Copyleft (L) 2005 by Sven Lindberg					   *
 *   k8055@k8055.mine.nu						   *
 *   Give it up already :) Simplified (read improved..) and included 	   *
 *   with k8055 lib and with a functional man page			   *
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *   This program is distributed in the hope that it will be useful,       *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU General Public License for more details.                          *
 *                                                                         *
 *   You should have received a copy of the GNU General Public License     *
 *   along with this program; if not, write to the                         *
 *   Free Software Foundation, Inc.,                                       *
 *   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             * 
 *                                                                         *
 *   Refined code for latest linux distributions by peterpt /google AI     *
 *   http://github.com/peterpt
 ***************************************************************************/
 
#include <string.h>
#include <stdio.h>
#include <stdlib.h> // Added for exit()
#include <stdbool.h> // Use modern standard for true/false
#include <sys/time.h>
#include "k8055.h"

#define STR_BUFF 256

// Global variables from original code
extern int DEBUG;
int ia1 = -1;
int ia2 = -1;
int id8 = -1;
int ipid = 0;
int numread = 1;
int debug = 0;
int dbt1 = -1;
int dbt2 = -1;
int resetcnt1 = false;
int resetcnt2 = false;
int delay = 0;

/*
	Convert a string on n chars to an integer
	Return  1 on sucess
			0 on failure (non number)
*/
int Convert_StringToInt(char *text, int *i)
{
	return sscanf(text, "%d", i);
}

/*
	Write help to standard output
*/
void display_help(char *params[])
{
	printf("K8055 version %s (Modernized Build)\n", Version());
	printf("Original copyrights (C) 2004-2005 by Sutre, Dempsey, Etelain, Nys, Lindberg\n");
	printf("\n");
	printf("Syntax : %s [-p:number] [-d:value] [-a1:value] [-a2:value]\n", params[0]);
	printf("             [-num:number] [-delay:number] [-dbt1:value]\n");
	printf("             [-dbt2:value] [-reset1] [-reset2] [-debug] [--help]\n");
	printf("\n");
	printf("    -p:<num>        Set board number (0-3)\n");
	printf("    -d:<val>        Set digital output value (0-255)\n");
	printf("    -a1:<val>       Set analog output 1 value (0-255)\n");
	printf("    -a2:<val>       Set analog output 2 value (0-255)\n");
	printf("    -num:<num>      Set number of reads to perform\n");
	printf("    -delay:<ms>     Set delay between reads (in milliseconds)\n");
	printf("    -dbt1:<ms>      Set debounce time for counter 1 (in milliseconds)\n");
	printf("    -dbt2:<ms>      Set debounce time for counter 2 (in milliseconds)\n");
	printf("    -reset1         Reset counter 1\n");
	printf("    -reset2         Reset counter 2\n");
	printf("    -debug          Activate debug mode\n");
	printf("    --help          Display this help text\n");
	printf("\n");
	printf("Output Format: (timestamp);(digital);(analog 1);(analog 2);(counter 1);(counter 2)\n");
	printf("Example: %s -p:0 -d:147 -a1:25 -a2:203\n", params[0]);
}

/*
	Read arguments, and store values
	Return true if arguments are valid
		else return false
*/
bool read_param(int argc, char *params[])
{
	bool erreurParam = false;
	int i;

	for (i = 1; i < argc; i++)
	{
		if (!strncmp(params[i], "-p:", 3) && !Convert_StringToInt(params[i] + 3, &ipid))
			erreurParam = true;
		else if (!strncmp(params[i], "-a1:", 4) && !Convert_StringToInt(params[i] + 4, &ia1))
			erreurParam = true;
		else if (!strncmp(params[i], "-a2:", 4) && !Convert_StringToInt(params[i] + 4, &ia2))
			erreurParam = true;
		else if (!strncmp(params[i], "-d:", 3) && !Convert_StringToInt(params[i] + 3, &id8))
			erreurParam = true;
		else if (!strncmp(params[i], "-num:", 5) && !Convert_StringToInt(params[i] + 5, &numread))
			erreurParam = true;
		else if (!strncmp(params[i], "-delay:", 7) && !Convert_StringToInt(params[i] + 7, &delay))
			erreurParam = true;
		else if (!strncmp(params[i], "-dbt1:", 6) && !Convert_StringToInt(params[i] + 6, &dbt1))
			erreurParam = true;
		else if (!strncmp(params[i], "-dbt2:", 6) && !Convert_StringToInt(params[i] + 6, &dbt2))
			erreurParam = true;
		else if (!strcmp(params[i], "-debug"))
		{
			debug = true;
			DEBUG = true;
		}
		else if (!strcmp(params[i], "-reset1"))
			resetcnt1 = true;
		else if (!strcmp(params[i], "-reset2"))
			resetcnt2 = true;
		else if (!strcmp(params[i], "--help"))
		{
			display_help(params);
			return false;
		}
	}

	if (debug)
	{
		fprintf(stderr, "Parameters: Card=%d Analog1=%d Analog2=%d Digital=%d\n", ipid, ia1, ia2, id8);
	}

	if (ipid < 0 || ipid > 3)
	{
		fprintf(stderr, "Error: Invalid board address! Must be between 0 and 3.\n");
		return false;
	}

	if (erreurParam)
	{
		fprintf(stderr, "Error: Invalid or incomplete options.\n\n");
		display_help(params);
		return false;
	}

	return true;
}

/*
	Give current timestamp in milliseconds.
    REMOVED 'inline' keyword to fix "undefined reference" linker error.
*/
unsigned long time_msec(void)
{
	struct timeval t;
	gettimeofday(&t, NULL); // Second argument (timezone) is obsolete, should be NULL.
	return (t.tv_sec * 1000) + (t.tv_usec / 1000);
}

int main(int argc, char *params[])
{
	int i, result;
	long d = 0;
	long a1 = 0, a2 = 0;
	long c1 = 0, c2 = 0;
	unsigned long start_time, measure_start_time, last_call_time = 0;

	start_time = time_msec();

	if (!read_param(argc, params))
	{
		return 1; // Exit if parameters are invalid
	}

	if (OpenDevice(ipid) < 0)
	{
		fprintf(stderr, "Error: Could not open the k8055 (address:%d).\n", ipid);
		fprintf(stderr, "Please ensure the device is connected and you have the correct permissions (check udev rules).\n");
		return -1;
	}

	if (resetcnt1)
		ResetCounter(1);
	if (resetcnt2)
		ResetCounter(2);
	if (dbt1 != -1)
		SetCounterDebounceTime(1, dbt1);
	if (dbt2 != -1)
		SetCounterDebounceTime(2, dbt2); // Fixed bug: was using dbt1 for both

	// Simplified setting values
	if (id8 != -1)
	{
		result = WriteAllDigital((long)id8);
		if (debug) printf("Set digital:%d => %d\n", id8, result);
	}
	if (ia1 != -1)
	{
		result = OutputAnalogChannel(1, ia1);
		if (debug) printf("Set analog1:%d => %d\n", ia1, result);
	}
	if (ia2 != -1)
	{
		result = OutputAnalogChannel(2, ia2);
		if (debug) printf("Set analog2:%d => %d\n", ia2, result);
	}

	measure_start_time = time_msec(); // Measure start
	for (i = 0; i < numread; i++)
	{
		if (delay > 0)
		{
			// Wait until next measure
			while (time_msec() - measure_start_time < (unsigned long)(i + 1) * delay);
		}

		ReadAllValues(&d, &a1, &a2, &c1, &c2);
		last_call_time = time_msec();
		
        // Use correct format specifiers (%lu for unsigned long, %ld for long) for safety
		printf("%lu;%ld;%ld;%ld;%ld;%ld\n",
			   last_call_time - start_time, d, a1, a2, c1, c2);
	}

	CloseDevice();
	return 0;
}
