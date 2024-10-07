![image](https://github.com/user-attachments/assets/389f06e8-ed29-4cb8-9a74-ebdbf8a08bf9)

Pivot Table generated from CSV
![image](https://github.com/user-attachments/assets/c5aaa368-33af-44ae-b0eb-917a15593364)



##  Summary
This program will connect to IN1804 and collect internal temperature data at a predefined schedule.  It is fully functional and will generate an output in a CSV file similar to what is shown above.


## Requirements
This program uses some non-standard Python libraries:
- PYTZ
- schedule


## Next Steps
1. Make the schedule timing a variable
2. Add indoor / outdoor temps into the CSV
3. Add Week/Day/Hour columns in CSV for easier table generation
4. Add Room # column in CSV
5. Show both Farenheit and Celsius in CSV
6. Convert into a class to be used in a larger system
7. Change In1 Signal...In4 Signal to show the input name (if consistent) and change the 1/0 to Active Signal or No Signal.
8. Add baseline max operating temp data for a reference line.
9. Fix the multi-threaded monitoring of responses
