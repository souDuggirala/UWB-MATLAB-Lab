function collectAndPlot()
    global status expName;
    status = "ST";
    
    %Intializing Ground truth var
    x_true = zeros(1,1);
    y_true = zeros(1,1);

    %Intializing Anchor postion var
    x_anch_pos = zeros(1,1);
    y_anch_pos = zeros(1,1);
    
    cleanup = onCleanup(@()myCleanup());
    try
        %Getting name of the experiment
        expName = input("Enter the name of the experiment: ",'s');
    
        %Checking if previous data of experiment is present
        if exist(expName+"/LastExpVar.mat", 'file')
            existingValues = input("Do you want to use existing experimental variables?(Y/N) ",'s');
        else
            existingValues = "N";
        end
        
        if(strcmpi(existingValues,"Y"))
            load(expName+"/LastExpVar","x_anch_pos","y_anch_pos","x_true","y_true");
            
        elseif(strcmpi(existingValues,"N"))
            %Getting time duration of positioning data collection, in minutes
            duration = input("Enter the time duration in minutes for each point: ");
            %Getting number of the positions
            positions = input("Enter the number of positions: ");
            %Getting number of anchors
            anchNumber = input("Enter the number of UWB anchors: ");

            %Ground truth
            x_true = zeros(1,positions);
            y_true = zeros(1,positions);

            %Anchor postion
            x_anch_pos = zeros(1,anchNumber);
            y_anch_pos = zeros(1,anchNumber);
            
            for i = 1:anchNumber
                xPrompt = sprintf("\t Enter x coordinate of anchor %d :", i);
                x_anch_pos(i) = input(xPrompt);
                yPrompt = sprintf("\t Enter y coordinate of anchor %d :", i);
                y_anch_pos(i) = input(yPrompt);        
            end

            %Getting coordinates of positions 
            method = input("Do you have actual coordinates of positions?(Y/N) ",'s');

            if(strcmpi(method,"Y"))
                for i = 1:positions 
                xPrompt = sprintf("\t Enter x coordinate of postion %d :", i);
                x_anch_pos(i) = input(xPrompt);
                yPrompt = sprintf("\t Enter y coordinate of postion %d :", i);
                y_anch_pos(i) = input(yPrompt);     
                end 

            elseif(strcmpi(method,"N"))
                disp("We will be using triangulation for getting coordinates.")
                
                allSame = input("Do you plan to use same anchors for reference?(Y/N) ",'s');
                if(strcmpi(allSame,"Y"))
                    anchorNumberPrompt = sprintf("\t Enter anchor number you want to use as "...
                        +"reference in order e.g. [1 2] or [1 2 3] for positions: ");
                    anchorNumber = input(anchorNumberPrompt);                    
                end

                for i = 1:positions
                    if(strcmpi(allSame,"N"))
                        anchorNumberPrompt = sprintf("\t Enter anchor number you want to use as "...
                        +"reference in order e.g. [1 2] or [1 2 3] for position %d : ", i);
                        anchorNumber = input(anchorNumberPrompt);
                    end    
                    distanceFromAnchorPrompt = sprintf("\t Enter distance "...
                    +"of tag from those anchor in same order [d1 d2] or [d1 d2 d3] for position %d : ", i);
                    distanceFromAnchor = input(distanceFromAnchorPrompt);
                    coordinates = triangulationForCordinates(anchorNumber,distanceFromAnchor,x_anch_pos,y_anch_pos);
                    x_true(i) = coordinates(1);
                    y_true(i) = coordinates(2);       
                end    
            end
        end 

        posAnchor = zeros(1,2*length(x_anch_pos));
        posAnchor(1:2:end) = x_anch_pos;posAnchor(2:2:end) = y_anch_pos;
        fprintf("\n\n Postion of archors in order " ); disp(1:1:length(x_anch_pos));
        fprintf("\t(%d,%d)",posAnchor);
        posTag = zeros(1,2*length(x_true));
        posTag(1:2:end) = x_true;posTag(2:2:end) = y_true;
        fprintf("\n\n Postion of tag(s) in order " ); disp(1:1:length(x_true));
        fprintf("\t(%d,%d)",posTag);
        
        %Writing files for the postions
        WritePosFile(positions,duration);
        
        GeoExp(x_anch_pos,y_anch_pos,x_true,y_true);
    
   catch ME
       
       fprintf("\n"+ME.identifier);
       delete(expName+"/*.mat")
       delete(expName+"/*.png")
       rethrow(ME)
       
   end
   status = "FT";

end

function WritePosFile(positions,duration)
    global expName;
    serialPort = input("Enter the serial port name (string): ",'s');
    s=serialport(serialPort,115200);
    mkdir (expName)
    cd (expName)
    for i = linspace(1,positions,positions)
        fileName="pos"+string(i)+".txt";
        disp(fileName);
        fileID = fopen(fileName,'w');
        tStart=tic;  %starts the timer
        flush(s);
        while(true)
            data = readline(s);
            fprintf(fileID,data+"\n");
            if(toc(tStart)>duration*60)
                disp("Done with the file");
                while(i~=positions)
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





function GeoExp(x_anch_pos,y_anch_pos,x_true,y_true)
    global expName;
    cd (expName)
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
    
    figure(1);
    histogram(Xerror);
    xlabel('Errors in X coordinate (m)');
    figure(2);
    saveas(gcf,'XERROR.png');
    histogram(Yerror);
    xlabel('Errors in Y coordinate (m)');
    saveas(gcf,'YERROR.png');
    save('Error','Xerror','Yerror');
    save("LastExpVar","x_anch_pos","y_anch_pos","x_true","y_true");
pos_plot(x_true, y_true, x_tag_pos_avg, y_tag_pos_avg, x_tag_pos_std,y_tag_pos_std,...
    x_anch_pos, y_anch_pos, expName);
pos_errorbar(x_true, y_true, x_tag_pos_avg, y_tag_pos_avg, x_tag_pos_std,y_tag_pos_std,...
    x_anch_pos, y_anch_pos, expName);

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
    figure(3);
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
        fill(x_s,y_s,'b','facealpha',0.3);
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
    plot_true_pos = plot(x_true, y_true, 'r*');
    % Plot the measured positions of tags
    plot_measured = plot(x_measure, y_measure,'ksq');
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
    figure(4);
    set(gcf,'unit','normalized','position',[0.2, 0.2, 0.5, 0.5]);
    ax=gca;
    ax.XTickMode = 'auto';
    ax.YTickMode = 'auto';
    e1 = errorbar(x_measure, y_measure, y_std, y_std, x_std, x_std,...
        'ksq');
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
    
    true_pos = plot(x_true, y_true, 'r*');
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


% function calculates the ground-truth tag coordinates 
% according to surveyed results in experiments (solving equation set)
% Options: two-point surveying & three-point surveying
function coordinates = triangulationForCordinates(aNum,ds,xAP,yAP)

    syms x y;
    coordinates = zeros(1,2);
    ref = length(aNum);

    if ref == 2
        x1 = xAP(aNum(1));y1 = yAP(aNum(1));x2 = xAP(aNum(2));y2 = yAP(aNum(2));
        d1 = ds(1); d2 = ds(2);
        eq1 = (x-x1)^2 + (y-y1)^2 == d1^2;
        eq2 = (x-x2)^2 + (y-y2)^2 == d2^2;
        
        if aNum(1) == 1
            S = solve(eq1,eq2,x>=x1,y>=y1);
        elseif aNum(1) == 2 
            S = solve(eq1,eq2,x<=x1,y>=y1);
        elseif aNum(1) == 3 
            S = solve(eq1,eq2,x<=x1,y<=y1);
        end
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
global expName status
fprintf('\n Close ALL \n');
fclose("all");
fprintf(status + "\n");
if ~strcmp(status,"FN")    
    delete(expName+"/*.mat")
    delete(expName+"/*.png")
end
cd ..
clear;
end
