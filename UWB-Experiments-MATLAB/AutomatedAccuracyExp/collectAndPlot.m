
function collectAndPlot()
    cleanup = onCleanup(@()myCleanup());
    %Getting time duration of positioning data collection, in minutes
    duration = input("Enter the time duration in minutes for each point: ");
    %Getting number of the experiment
    postions = input("Enter the number of postions: ");
    %Getting name of the experiment
    expName = input("Enter the name of the experiment: ",'s');
    %Getting number of anchors
    anchNumber = input("Enter the number of UWB anchors: ");
    
    %Ground truth
    x_true = zeros(1,postions);
    y_true = zeros(1,postions);

    %Anchor postion
    x_anch_pos = zeros(1,anchNumber);
    y_anch_pos = zeros(1,anchNumber);
    
    for i = 1:anchNumber 
        x_anch_pos(i) = input("Enter x coordinate of anchor " + i + ": "); 
        y_anch_pos(i) = input("Enter y coordinate of anchor " + i + ": ");        
    end
    
    %Getting coordinates of postions 
    method = input("Do you have actual coordinates of postions?(Y/N) ",'s');
    
    if(method == 'Y'||method == 'y')
        for i = 1:postions 
            x_true(i) = input("Enter x coordinate of postion " + i + ": "); 
            y_true(i) = input("Enter y coordinate of postion " + i + ": ");
        end 
        
    elseif(method == 'N'||method == 'n')   
        disp("\tWe will be using triangulation for getting coordinates.")
    
        for i = 1:postions
            anchorNumber = input("\tEnter anchor number you want to use as reference in order e.g. [1 2] or [1 2 3] for postion "+i+": " );
            distanceFromAnchor = input("\tEnter distance of tag from those anchor in same order [d1 d2] or [d1 d2 d3] for postion "+i+": " );
            coordinates = triangulationForCordinates(anchorNumber,distanceFromAnchor,x_anch_pos,y_anch_pos);
            x_true(i) = coordinates(1);
            y_true(i) = coordinates(2);       
        end    
    end
    
    disp("Ground truth tag position(s): ");
    disp([x_true; y_true]);
    disp("Anchor position(s): ");
    disp([x_anch_pos; y_anch_pos]);
    WritePosFile(postions,expName,duration);
    GeoExp(expName,x_anch_pos,y_anch_pos,x_true,y_true);

end

function WritePosFile(postions,expName,duration)
    %postions = input("Enter the number of postions ");
    serialPort = input("Enter the serial port name (string): ",'s');
    s=serialport(serialPort,115200);
    mkdir (expName)
    cd (expName)
    for i = linspace(1,postions,postions)
        fileName="pos"+string(i)+".txt";
        disp(fileName);
        fileID = fopen(fileName,'w');
        tStart=tic;  %starts the timer
        while(true)
            data = readline(s);
            fprintf(fileID,data+"\n");
            if(toc(tStart)>duration*60)
                disp("Done with the file");
                while(i~=postions)
                    confirmation = input("Please confirm location tag is changed? (Y/N) ", 's');    
                    if(confirmation=="Y"||confirmation=="y")
                        break;
                    else
                        continue;
                    end   
                end
                break;
            end          
        end
    end
    fclose("all");
    cd ..
end





function GeoExp(name,x_anch_pos,y_anch_pos,x_true,y_true)
    % %Anchor Positions for height exp
    cd (name)
    dinfo = dir('pos*.txt');
    filenames = {dinfo.name};
    Xerror=zeros(1,1);
    Yerror=zeros(1,1);
    x_tag_pos_avg=zeros(1,length(filenames));
    y_tag_pos_avg=zeros(1,length(filenames));
    x_tag_pos_std=zeros(1,length(filenames));
    y_tag_pos_std=zeros(1,length(filenames));
    for K = 1 : length(filenames)
        thisfile = filenames{K};
        display(thisfile);
        %read the raw file as matrix first row is ignored
		pos1 = readmatrix(thisfile);
        %extracted X and Y coordinates from the file 
		pos1 = pos1(:,4:5);
		pos1 = pos1(all(~isnan(pos1),2),:);
        Xerror = [Xerror;(pos1(:,1) - x_true(K))];
        Yerror = [Yerror;(pos1(:,2) - y_true(K))];
        avgPos1 = mean(pos1);
        stdPos1 = std(pos1);
        x_tag_pos_avg(1,K) = avgPos1(1,1);
        y_tag_pos_avg(1,K) = avgPos1(1,2);
        x_tag_pos_std(1,K) = stdPos1(1,1);
        y_tag_pos_std(1,K) = stdPos1(1,2);
    end
    
    figure(1)
    histogram(Xerror);
    xlabel('Errors in X coordinate (m)');
    figure(2)
    xlabel('Errors in Y coordinate (m)');
    histogram(Yerror);
    save('Error','Xerror','Yerror')

pos_plot(x_true, y_true, x_tag_pos_avg, y_tag_pos_avg, x_tag_pos_std,y_tag_pos_std,...
    x_anch_pos, y_anch_pos, name);
pos_errorbar(x_true, y_true, x_tag_pos_avg, y_tag_pos_avg, x_tag_pos_std,y_tag_pos_std,...
    x_anch_pos, y_anch_pos, name);
end



function pos_plot(x_true, y_true, x_measure, y_measure, x_std, y_std, ...
    x_anch, y_anch, title_name)
    % function call to plot according to different data, using oval for std.
    % NO NEED TO COMMENT/UNCOMMENT
    % Display plot while done
    
%     % To be used for blockage scenario
%     BLOCKAGE1_POS = [0.1, 0.98,0.02,0.3];
%     BLOCKAGE2_POS = [2.2, 0.98,0.02,0.3];
    axs = computeAxisLim(x_anch, y_anch);
    figure();
    box on;
    set(gcf,'unit','normalized','position',[0.2, 0.2, 0.5, 0.5]);
    ax=gca;
    ax.XTickMode = 'auto';
    ax.YTickMode = 'auto';
    hold on;
    % Plot the dummy handles for legend
    std_1 = plot(nan, nan, 'bo', 'MarkerFaceColor','b');
    %buff = plot(nan, nan, 'LineStyle','--', 'Color','m');

    % Plot the std. deviation for all data points
    for i = 1:1:length(x_true)
        theta = 0 : 0.01 : 2*pi;
        xcenter = x_measure(i);
        ycenter = y_measure(i);
        xradius = x_std(i);
        yradius = y_std(i);
        x_s = xradius * cos(theta) + xcenter;
        y_s = yradius * sin(theta) + ycenter;
        h = fill(x_s,y_s,'b','facealpha',0.3);
        hold on
    end

    % Plot the connection from truth to measurements
    for i = 1:1:length(x_true)
        quiver(x_true(i), y_true(i), ...
            x_measure(i)-x_true(i), ...
            y_measure(i)-y_true(i),...
            'color','k','LineStyle',':','LineWidth',0.3);
        hold on
    end

    % Plot the anchor positions
    anch = plot(x_anch, y_anch, 'b^');
    % Plot the buffer (+-10cm) for decawave
    centers = [x_true' y_true'];
    radii = repelem(0.1,length(x_true),1);
    disp(centers);
    disp(radii);
    buff=viscircles(centers,radii,'LineStyle','--','Color','m');
    
    if(contains(title_name,"Blocked"))
        % Need to specify the BLOCKAGE*_POS
        % TODO(none-urgent): Provide a flexible interface to allow
        % different number of blockages (and their positions)
        rectangle('Position',BLOCKAGE1_POS, 'EdgeColor','k', 'FaceColor', 'k', 'Curvature', 0.2,'LineWidth',0.3);
        rectangle('Position',BLOCKAGE2_POS, 'EdgeColor','k', 'FaceColor', 'k', 'Curvature', 0.2,'LineWidth',0.3);
    end
    % Plot the true positions of tags
    plot_true_pos = plot(x_true, y_true, 'r.-','LineWidth',1);
    % Plot the measured positions of tags
    plot_measured = plot(x_measure, y_measure,'b-','LineWidth',2);
    axis(axs);
    daspect([1 1 1]);
    grid on;
    l = legend([plot_true_pos,plot_measured,std_1,anch,buff],...
        'True Position','Measured Position','Standard Deviation (Oval)',...
        'Anchor', 'Accuracy Buffer (+-0.1m)');
    set(l, 'Location', 'southeast');
    title(title_name);
    xlabel('X coordinate (m)');
    ylabel('Y coordinate (m)');
    hold off;
    legend boxon

end



function pos_errorbar(x_true, y_true, x_measure, y_measure, x_std, y_std, ...
    x_anch, y_anch, title_name)
    % function call to plot according to different data, using errorbar for std.
    % NO NEED TO COMMENT/UNCOMMENT
    % Display plot while done
    
%     % To be used for blockage scenario
%     BLOCKAGE1_POS = [0.1, 0.98,0.02,0.3];
%     BLOCKAGE2_POS = [2.2, 0.98,0.02,0.3];
      
    axs = computeAxisLim(x_anch, y_anch);
    figure();
    set(gcf,'unit','normalized','position',[0.2, 0.2, 0.5, 0.5]);
    ax=gca;
    ax.XTickMode = 'auto';
    ax.YTickMode = 'auto';
    e1 = errorbar(x_measure, y_measure, y_std, y_std, x_std, x_std,...
        'Marker','o','LineStyle','-','LineWidth',2);
    hold on;
    % Plot the anchor positions
    anch = plot(x_anch, y_anch, 'b^');
    % Plot the buffer (+-10cm) for decawave
    centers = [x_true' y_true'];
    radii = repelem(0.1,length(x_true),1);
    buff=viscircles(centers,radii,'LineStyle','--','Color','m');
    
    if(contains(title_name,"Blocked"))
        % Need to specify the BLOCKAGE*_POS
        % TODO(none-urgent): Provide a flexible interface to allow
        % different number of blockages (and their positions)
        rectangle('Position',BLOCKAGE1_POS, 'EdgeColor','k', 'FaceColor', 'k', 'Curvature', 0.2,'LineWidth',0.3);
        rectangle('Position',BLOCKAGE2_POS, 'EdgeColor','k', 'FaceColor', 'k', 'Curvature', 0.2,'LineWidth',0.3);
    end
    
    true_pos = plot(x_true, y_true, 'r.-','LineWidth',1);
    % Plot the connection from truth to measurements
    for i = 1:1:length(x_true)
        quiver(x_true(i), y_true(i), ...
            x_measure(i)-x_true(i), ...
            y_measure(i)-y_true(i),...
            'color','k','LineStyle',':','LineWidth',0.3);
        hold on
    end
    daspect([1 1 1]);
    grid on;
    l = legend([true_pos,e1,buff,anch],'True Position','Measured Position','Accuracy Buffer (+-0.1m)','Anchor');
    set(l, 'Location', 'southeast');
    axis(axs);
    title(title_name);
    xlabel('X coordinate (m)');
    ylabel('Y coordinate (m)');
    
end


function coordinates = triangulationForCordinates(aNum,ds,xAP,yAP)
    % function call to calculate the ground-truth tag coordinates 
    % according to surveyed results in experiments (solving equation set)
    % Options: two-point surveying & three-point surveying
    syms x y;
    coordinates = zeros(1,2);
    ref = length(aNum);
    % disp(coordinates);
    % disp(aNum);
    % disp(ds);
    % disp(xAP);
    % disp(yAP);
    % disp(ref);

    if ref == 2
        x1 = xAP(aNum(1));y1 = yAP(aNum(1));x2 = xAP(aNum(2));y2 = yAP(aNum(2));
        d1 = ds(1); d2 = ds(2);
        eq1 = (x-x1)^2 + (y-y1)^2 == d1^2;
        eq2 = (x-x2)^2 + (y-y2)^2 == d2^2;
        S = solve(eq1,eq2,x>x1,y>y1);
        coordinates = [double(S.x) double(S.y)];


    elseif ref == 3
        x1 = xAP(aNum(1));y1 = yAP(aNum(1));x2 = xAP(aNum(2));y2 = yAP(aNum(2));
        x3 = xAP(aNum(3));y3 = yAP(aNum(3));
        d1 = ds(1); d2 = ds(2);d3 = ds(3);
        eq1 = (x-x1)^2 + (y-y1)^2 == d1^2;
        eq2 = (x-x2)^2 + (y-y2)^2 == d2^2;
        eq3 = (x-x3)^2 + (y-y3)^2 == d3^2;
        S = solve(eq1,eq2,eq3);
        coordinates = [double(S.x) double(S.y)];    
    end


end

function ax = computeAxisLim(x_anch,y_anch)
    % Specify the axis limits of the plot according to the range of anchors
    ax=zeros(1,4);
    ax(1) = min(x_anch)-5;
    ax(2) = max(x_anch)+5;
    ax(3) = min(y_anch)-5;
    ax(4) = max(y_anch)+5;
end

function myCleanup()
    disp('Close ALL');
    fclose("all");
    clear;
    cd ..
end
