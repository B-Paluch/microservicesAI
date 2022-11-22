package com.example.newproj.entity;

import lombok.*;

@AllArgsConstructor
@RequiredArgsConstructor
@Getter
@Setter
@Builder
public class ResponseFileEntity {
    private String name;
    private String url;
    private String type;
    private long size;
}
