files = dir('interp*.dat');
a={};
for i = 1 : length(files)
    a{i} = load(files(i).name);
end
figure
hold on
for i=1 : length(files)
    if files(i).name == 'interp_trace_0.dat'
        continue
    end
    b=a{i};
    plot(b(:,1), b(:,2))
end

        