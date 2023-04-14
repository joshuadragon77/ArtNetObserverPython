import requests;
import time;
import math;
import sys;

if (__name__ == "__main__"):
    arguments = sys.argv;

    if (len(arguments) <= 1):
        print("ArtNet Reciever.");
        print("Arguments: ");
        print(" [ Host ][ WebPort (Default: 9090) ][ Universe (Default: 1) ] [ Start Channel Index (Default: 0) ] [End Channel Index (Default: 512) ]");
        print("Universe - Creates a ArtNet Stupid Server that recieves ArtNet data from that specific universe number");
        print("Start Channel Index - The left slice position of the raw data recieved");
        print("End Channel Index - The right slice position of the raw data recieved");

        print("\nExamples:");
        print("python3 main.py localhost 9090 1 0 512");
        print("Listens on universe 0, includes all channel");
        exit(0);
    
    host = "localhost";
    if (len(arguments) >= 2):
        host = arguments[1];
    port = 9090;
    if (len(arguments) >= 3):
        port = int(arguments[2]);
    universe = 1;
    if (len(arguments) >= 4):
        universe = int(arguments[3]);
    from_slice = 0;
    if (len(arguments) >= 5):
        from_slice = int(arguments[4]);
    to_slice = 512;
    if (len(arguments) >= 6):
        to_slice = int(arguments[5]);
    
    # previous_data = [0] * 512;

    max_changes = 1;
    
    def new_data(data):
        global max_changes;

        image = "\x1B[1J\nNew Data:\n\n";

        seen_index = len(data);

        for index in range(from_slice, min(len(data), to_slice + 1)):
            if (data[index] != 0):
                seen_index = index;
                break;

        image += f"Raw Data Slice: [{seen_index}, {len(data)}]\nUser Selected Slice: [{from_slice},{to_slice}]\n\n";

        image += "Channel Changes: \n";

        changes = 0;

        for index in range(from_slice, min(len(data), to_slice + 1)):
            if (data[index] != 0 and changes < 10):
                changes += 1;
                image += f"\t[Channel {index}]: {data[index]}\n";
        
        max_changes = max(max_changes, changes);

        for index in range(0, max_changes - changes):
            image += "\n";

        image += "\n";

        starting_y = math.floor(from_slice/40);
        ending_y = math.ceil(to_slice/40);

        image += "     ";

        for x in range(0, 40):
            if (x%5 == 0):
                image += str(math.floor(x / 10));
            else:
                image += " ";
        
        image += "\n     ";

        for x in range(0, 40):
            if (x%5 == 0):
                image += str(x % 10);
            else:
                image += " ";

        image += "\n";

        for y in range(starting_y, ending_y):
            image += "{0:3d} |".format(y * 40);

            for x in range(0, 40):
                index = y * 40 + x;
                value = 0;
                
                if (from_slice <= index <= to_slice and index < len(data)):
                    value = data[index] / 255;

                    g = round(255 * value);
                    b = round(85 * value);

                    image += f"\x1B[48;2;0;{g};{b}m ";
                else:
                    image += f"\x1B[0m ";
            
            image += "\x1B[0m\n";
        
        print(image);
        
        print(f"\nListening on Universe {universe}...");
        print("-------------------------------");
        print("Press CTR + C to End Listening Session");
        
    print(f"Listening on Universe {universe}...");
    print("-------------------------------");
    print("Press CTR + C to End Listening Session");

    while (True):

        response = requests.get(f"http://{host}:{port}/get_dmx?u={universe}");
        data = response.json();
        channels = data["dmx"];
        
        if (data["error"] != ""):
            print(data["error"]);
            exit(1);
        else:
            new_data(channels);

        time.sleep(.25);


