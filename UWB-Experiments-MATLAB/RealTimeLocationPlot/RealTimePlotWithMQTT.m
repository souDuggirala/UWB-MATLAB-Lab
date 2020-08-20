function RealTimePlotWithMQTT()
cleanup = onCleanup(@()myCleanup(M));
x_anch=[0,7.4,7.4,0];
y_anch=[0,0,7.4,7.4];
count = 0;
temp=0;
M = mqtt('tcp://172.16.46.92');
mysub = subscribe(M,'dwm/node/d605/uplink/location');
pause(1);
while (1)
        msg = read(mysub);
        position = jsondecode(msg);
        if(count~=0)
            if (temp==position.superFrameNumber)
               disp("Value Not updated") 
               
            else
                disp( count + " " + position.position.x + " " + position.position.y)    
                if(~(strcmp(position.position.x,"NaN")&&strcmp(position.position.y,"NaN")))
                    check = geofencing(position.position.x,position.position.y);
                    if(check)
                        disp("OUTSIDE" + " " + position.position.x + " " + position.position.y)
                    end
                end
            end
        end
        count = count+1;
        temp = position.superFrameNumber;
        disp(position.superFrameNumber)
        pause(0.1)
end
end



function check = geofencing(X,Y)
check = false;
if ((X < 1) || (Y < 1)|| (X > 7.0)|| (Y>7.0))
   check=true; 
end
end


function myCleanup(M)
disp('Close MQTT');
delete(M);
end

