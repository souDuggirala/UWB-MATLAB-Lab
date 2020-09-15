function RealTimePlotWithMQTT()
ip1 = 'tcp://192.168.200.133';
ip2 = 'tcp://192.168.207.39';
link = 'Tag/+/Uplink/Location';
getData(ip1,ip2,link);
cleanup = onCleanup(@()myCleanup());
end


function getData(ip1,ip2,link)
M1=0;
M2=0;
ME = MException('myComponent:inputErrorMQTT', ...
'Data received is not updated reconnecting');
error = false;
try 
    disp("reached");
    %M1 = mqtt(ip1);
    M2 = mqtt(ip2);
    %mysub1 = subscribe(M1,link);
    mysub2 = subscribe(M2,link);
    pause(1);
    count = 0;
    while (1)
        disp(count)
            %msg1 = read(mysub1);
            msg2 = read(mysub2);
            %position1 = jsondecode(msg1);
            position2 = jsondecode(msg2);
            %tag1=extractBetween(position1.tag_id,strlength(position1.tag_id)-4,strlength(position1.tag_id));
            tag2=extractBetween(position2.tag_id,strlength(position2.tag_id)-4,strlength(position2.tag_id));
            if(count~=0)
%                 disp(position1.superFrameNumber)
%                 if (temp1==position1.superFrameNumber)
%                     disp('Trouble reading from mqtt')
%                     beep;
%                     error = true;
% 
%                 else  
%                     if(~(strcmp(position1.est_pos.x,"NaN")&&strcmp(position1.est_pos.y,"NaN")))
%                         check = geofencing(position1.est_pos.x,position1.est_pos.y);
%                         if(check)
%                             disp(tag1+" OUTSIDE" + " " + position1.est_pos.x + " " + position1.est_pos.y)
%                         else
%                             disp(tag1+" INSIDE" + " " + position1.est_pos.x + " " + position1.est_pos.y)
%                         end
%                     end
%                 end
                
                disp(position2.superFrameNumber)
              disp('Data received is not updated reconnecting')  if (temp2==position2.superFrameNumber)
                    
                    error = true;

                else  
                    if(~(strcmp(position2.est_pos.x,"NaN")&&strcmp(position2.est_pos.y,"NaN")))
                        check = geofencing(position2.est_pos.x,position2.est_pos.y);
                        if(check)
                            disp(tag2+" OUTSIDE" + " " + position2.est_pos.x + " " + position2.est_pos.y)
                        else
                            disp(tag2+" INSIDE" + " " + position2.est_pos.x + " " + position2.est_pos.y)
                        end
                    end
                end
            end
            count = count+1;
            %temp1 = position1.superFrameNumber;
            temp2 = position2.superFrameNumber;
            disp( " " + temp2);
            pause(0.1)
            if(error)
                %delete(M1);
                delete(M2);
                throw(ME);
            end
            
            pause(1);
    end
catch ME
    disp(ME);
    if contains(lower(ME.identifier), lower("MQTT"))
            getData(ip1,ip2,link);
    end
end
end


function check = geofencing(X,Y)
check = false;
if ((X < 1) || (Y < 1)|| (X > 7.0)|| (Y>7.0))
   check=true; 
end
end


function myCleanup()
disp('Close MQTT');
close all;
end

